# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DepthReaderOCR - Versão 1.1.0
 Detecta números rotacionados em cartas náuticas
                              -------------------
        begin                : 2025-06-21
        copyright            : (C) 2025 by Elivaldo Rocha
        email                : carvalhovaldo09@gmail.com
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QThread, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog, QApplication, QInputDialog
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsProject, QgsCoordinateTransform, QgsMessageLog, Qgis

import csv
import numpy as np
import os.path
import logging
import warnings
import re

# ============== SISTEMA DE DEPENDÊNCIAS ==============
from .dependency_manager import DependencyChecker

# Imports opcionais - só importa se estiver disponível
OPENCV_AVAILABLE = False
TESSERACT_AVAILABLE = False
EASYOCR_AVAILABLE = False
PIL_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
    print("✅ OpenCV disponível")
except ImportError:
    cv2 = None
    print("❌ OpenCV não disponível")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ PyTesseract disponível")
except ImportError:
    pytesseract = None
    print("❌ PyTesseract não disponível")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✅ EasyOCR disponível")
except ImportError:
    easyocr = None
    print("❌ EasyOCR não disponível")

try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("✅ PIL disponível")
except ImportError:
    Image = None
    print("❌ PIL não disponível")

try:
    from osgeo import gdal
    print("✅ GDAL disponível")
except ImportError:
    QgsMessageLog.logMessage("❌ GDAL não disponível - isso é um problema sério!", "DepthReaderOCR", Qgis.Critical)
# ============== FIM DO SISTEMA DE DEPENDÊNCIAS ==============

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .deep_reader_ocr_dialog import DepthReaderOCRDialog

# Configuração do Tesseract para Windows (só se disponível)
if TESSERACT_AVAILABLE and pytesseract:
    try:
        config_file = os.path.join(os.path.expanduser('~'), 'tesseract_config.txt')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                pytesseract.pytesseract.tesseract_cmd = f.read().strip()
        else:
            # Tenta caminhos comuns no Windows
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    except Exception as e:
        QgsMessageLog.logMessage(f"Erro na configuração do Tesseract: {e}", "DepthReaderOCR", Qgis.Warning)
        pytesseract.pytesseract.tesseract_cmd = None


# ============== CLASSE PARA PROCESSAMENTO EM BACKGROUND ==============
class OCRWorkerThread(QThread):
    """Thread para processamento OCR em background com feedback de progresso"""
    
    progress_update = pyqtSignal(str, int)
    result_ready = pyqtSignal(int, float, float)
    error_occurred = pyqtSignal(str)
    
    # SUGESTÃO: Preparação para Parâmetros Configuráveis
    # O construtor agora aceita os parâmetros de OCR para que não sejam fixos.
    def __init__(self, click_tool, img_data_raw, x_m, y_m, rotations, preprocess_methods):
        super().__init__()
        self.click_tool = click_tool
        self.img_data_raw = img_data_raw
        self.x_m = x_m
        self.y_m = y_m
        self.is_cancelled = False
        # Armazena os parâmetros recebidos
        self.rotations = rotations
        self.preprocess_methods = preprocess_methods
    
    def cancel(self):
        self.is_cancelled = True
    
    def run(self):
        try:
            self.progress_update.emit("🧠 Carregando motor EasyOCR...", 3)
            self.click_tool._get_easyocr_reader()
            if self.is_cancelled:
                return

            self.progress_update.emit("🔍 Preparando imagem para análise...", 5)
            self.msleep(200)
            
            if self.is_cancelled:
                return
            
            if len(self.img_data_raw.shape) == 3:
                gray = cv2.cvtColor(self.img_data_raw, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.img_data_raw
            
            self.progress_update.emit("📐 Configurando rotações e filtros...", 10)
            self.msleep(100)
            
            if self.is_cancelled:
                return
            
            # SUGESTÃO: Preparação para Parâmetros Configuráveis
            # Usa os parâmetros recebidos em vez de valores fixos.
            rotations = self.rotations
            preprocess_methods = self.preprocess_methods
            
            self.progress_update.emit("🔬 Aumentando resolução da imagem...", 15)
            scale_factor = 2
            new_width = int(gray.shape[1] * scale_factor)
            new_height = int(gray.shape[0] * scale_factor)
            upscaled_gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            if self.is_cancelled:
                return
            
            all_results = []
            total_iterations = len(rotations) * len(preprocess_methods)
            current_iteration = 0
            best_angle_debug_saved = False
            
            for angle in rotations:
                if self.is_cancelled:
                    return
                
                center = (upscaled_gray.shape[1] // 2, upscaled_gray.shape[0] // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated_upscaled = cv2.warpAffine(
                    upscaled_gray, M, 
                    (upscaled_gray.shape[1], upscaled_gray.shape[0]),
                    borderMode=cv2.BORDER_CONSTANT,
                    borderValue=255
                )
                
                for pp_name, pp_func in preprocess_methods.items():
                    if self.is_cancelled:
                        return
                    
                    current_iteration += 1
                    progress_percent = 20 + int((current_iteration / total_iterations) * 60)
                    
                    if angle == 0:
                        angle_msg = "↗️ Analisando orientação normal"
                    elif angle > 0:
                        angle_msg = f"🔄 Rotacionando +{angle}° (horário)"
                    else:
                        angle_msg = f"🔄 Rotacionando {angle}° (anti-horário)"
                    
                    filter_name = pp_name.replace("adaptive_thresh_", "").replace("_", " ")
                    self.progress_update.emit(f"{angle_msg}\n🎛️ Filtro: {filter_name}", progress_percent)
                    
                    processed_img = pp_func(rotated_upscaled)
                    
                    if not best_angle_debug_saved:
                        self.click_tool._save_debug_data(processed_img, self.x_m, self.y_m, f"processed_{pp_name}_{angle}")
                        best_angle_debug_saved = True
                    
                    if self.is_cancelled:
                        return
                    
                    if EASYOCR_AVAILABLE:
                        self.progress_update.emit(f"🤖 EasyOCR analisando {angle}°...\n🎛️ Filtro: {filter_name}", progress_percent)
                        easyocr_results = self.click_tool._perform_ocr_easyocr(processed_img)
                        for text, method, confidence in easyocr_results:
                            all_results.append((text, method, angle, pp_name, confidence, len(text)))
                            print(f"🔄 Rot {angle:+4d}° PP {pp_name}: {method} detectou '{text}' (conf: {confidence:.2f}, len: {len(text)})")
                    
                    if self.is_cancelled:
                        return
                    
                    if self.click_tool.tesseract_available:
                        self.progress_update.emit(f"🔤 Tesseract analisando {angle}°...\n🎛️ Filtro: {filter_name}", progress_percent)
                        tesseract_results = self.click_tool._perform_ocr_tesseract(processed_img)
                        for text, method, confidence in tesseract_results:
                            all_results.append((text, method, angle, pp_name, confidence, len(text)))
                            print(f"🔄 Rot {angle:+4d}° PP {pp_name}: {method} detectou '{text}' (conf: {confidence:.2f}, len: {len(text)})")
                    
                    self.msleep(50)
            
            if self.is_cancelled:
                return
            
            self.progress_update.emit("🧮 Analisando resultados e calculando scores...", 85)
            self.msleep(200)
            
            if self.is_cancelled:
                return
            
            self.progress_update.emit("🎯 Selecionando melhor resultado...", 95)
            result = self.click_tool._process_all_results(all_results)
            
            self.progress_update.emit("✅ Análise concluída com sucesso!", 100)
            self.msleep(300)
            
            self.result_ready.emit(result, self.x_m, self.y_m)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class DepthReaderOCR:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DepthReaderOCR_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Depth Reader OCR')
        self.first_start = None
        self.dependencies_ok = False
        self.dependency_checker = DependencyChecker(self.iface.mainWindow())

    def tr(self, message):
        return QCoreApplication.translate('DepthReaderOCR', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True,
                   add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/deep_reader_ocr/icon.png'
        self.add_action(icon_path, text=self.tr(u'Depth Reader OCR'), callback=self.run, parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Depth Reader OCR'), action)
            self.iface.removeToolBarIcon(action)

    def _check_and_install_dependencies(self):
        try:
            has_minimum, missing_packages = self.dependency_checker.has_minimum_requirements()
            if has_minimum:
                QgsMessageLog.logMessage("✅ Dependências mínimas OK", "DepthReaderOCR", Qgis.Success)
                return True
            QgsMessageLog.logMessage(f"❌ Dependências faltando: {missing_packages}", "DepthReaderOCR", Qgis.Warning)
            if self.dependency_checker.prompt_installation(missing_packages):
                success = self.dependency_checker.install_packages(missing_packages)
                if success:
                    QMessageBox.information(
                        self.iface.mainWindow(),
                        "Instalação Concluída",
                        "✅ Dependências instaladas com sucesso!\n\n" +
                        "🔄 IMPORTANTE: REINICIE o QGIS para que as mudanças tenham efeito.\n\n" +
                        "🎉 Após reiniciar, o plugin estará pronto para uso!"
                    )
                return success
            else:
                instructions = self.dependency_checker.get_manual_instructions(missing_packages)
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Instalação Manual Necessária",
                    "❌ Plugin não pode funcionar sem as dependências.\n\n" + instructions
                )
                return False
        except Exception as e:
            QgsMessageLog.logMessage(f"Erro ao verificar dependências: {e}", "DepthReaderOCR", Qgis.Critical)
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Erro no Sistema de Dependências",
                f"Erro inesperado: {e}\n\n" +
                "💡 Tente instalar manualmente:\n" +
                "pip install opencv-python pytesseract easyocr Pillow"
            )
            return False

    def run(self):
        """Exibe o diálogo de configurações e ativa a ferramenta de clique se confirmado."""
        
        if not self.dependencies_ok:
            QgsMessageLog.logMessage("🔍 Verificando dependências...", "DepthReaderOCR", Qgis.Info)
            self.dependencies_ok = self._check_and_install_dependencies()
            if not self.dependencies_ok:
                return
        
        self.dialog = DepthReaderOCRDialog()
        if self.dialog.exec_():
            # --- INÍCIO DA ALTERAÇÃO ---
            # Lê todas as configurações da janela de diálogo
            debug_dir = self.dialog.get_debug_directory()
            csv_path = self.dialog.get_csv_path()
            clip_size = self.dialog.get_clip_size()
            use_ocr = self.dialog.get_use_ocr_mode()

            # SUGESTÃO: Lê os novos parâmetros configuráveis diretamente da interface!
            rotations_config = self.dialog.get_rotations()
            filters_config = self.dialog.get_preprocess_methods_config()
            
            # Constrói o dicionário de métodos de pré-processamento com base na seleção do usuário
            preprocess_methods_config = {}
            temp_tool = ClickTool(self.iface.mapCanvas(), self.iface, None, None, None, False) # Usado para acessar os métodos
            if filters_config.get("clahe"):
                preprocess_methods_config["clahe"] = temp_tool._preprocess_clahe
            if filters_config.get("gaussian"):
                preprocess_methods_config["adaptive_thresh_gaussian"] = lambda img: temp_tool._preprocess_adaptive_threshold(img, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 11, 2)
            if filters_config.get("mean"):
                preprocess_methods_config["adaptive_thresh_mean"] = lambda img: temp_tool._preprocess_adaptive_threshold(img, cv2.ADAPTIVE_THRESH_MEAN_C, 11, 2)
            # --- FIM DA ALTERAÇÃO ---

            canvas = self.iface.mapCanvas()
            self.tool = ClickTool(
                canvas, self.iface, debug_dir, csv_path, clip_size, use_ocr,
                rotations_config, preprocess_methods_config  # Passa os parâmetros lidos da UI
            )
            canvas.setMapTool(self.tool)
            
            if use_ocr:
                message = ("✅ Ferramenta de clique ativada!\n\n" +
                           "🤖 Modo: Visão Computacional (OCR)\n" +
                           "🖱️ Clique no mapa para detectar profundidades automaticamente.")
            else:
                message = ("✅ Ferramenta de clique ativada!\n\n" +
                           "✋ Modo: Entrada Manual\n" +
                           "🖱️ Clique no mapa e digite a profundidade manualmente.")
            
            QMessageBox.information(self.iface.mainWindow(), "Depth Reader OCR", message)
        else:
            QMessageBox.information(self.iface.mainWindow(), "Depth Reader OCR", "❌ Configuração cancelada. Ferramenta não ativada.")


class ClickTool(QgsMapToolEmitPoint):
    OCR_FAILED = -9999
    # SUGESTÃO: Constantes para o algoritmo de scoring.
    # Torna o código mais legível e fácil de ajustar.
    COMMON_DEPTH_BONUS = 1.5
    UNCOMMON_DEPTH_PENALTY = 0.8
    TEXT_LENGTH_BONUS_FACTOR = 0.1

    # SUGESTÃO: Preparação para Parâmetros Configuráveis
    # O construtor agora aceita os parâmetros de OCR.
    def __init__(self, canvas, iface, debug_dir, csv_path, clip_size, use_ocr=True, rotations=None, preprocess_methods=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.debug_dir = debug_dir
        self.csv_path = csv_path
        self.clip_size = clip_size
        self.use_ocr = use_ocr
        self.easyocr_reader = None
        self.tesseract_available = False
        self.progress_dialog = None
        self.worker_thread = None
        self.user_cancelled = False
        self.analysis_completed = False
        
        # Armazena os parâmetros recebidos
        self.rotations = rotations if rotations is not None else [-90, -45, 0, 45, 90]
        self.preprocess_methods = preprocess_methods if preprocess_methods is not None else {
            "clahe": self._preprocess_clahe,
            "adaptive_thresh_gaussian_11_2": lambda img: self._preprocess_adaptive_threshold(img, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 11, 2),
        }
        
        logging.getLogger('easyocr').setLevel(logging.ERROR)
        self.common_depths = set(range(1, 100 + 1)) 
        if 11 in self.common_depths:
            self.common_depths.remove(11)

        self._check_tesseract()

    def _get_easyocr_reader(self):
        if self.easyocr_reader is None and EASYOCR_AVAILABLE:
            try:
                old_level = logging.getLogger().level
                logging.getLogger().setLevel(logging.ERROR)
                warnings.filterwarnings("ignore")
                try:
                    self.easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                finally:
                    logging.getLogger().setLevel(old_level)
                    warnings.resetwarnings()
            except Exception as e:
                print(f"Erro ao inicializar EasyOCR: {e}")
                self.easyocr_reader = None
        return self.easyocr_reader

    def _check_tesseract(self):
        if not hasattr(self, '_tesseract_checked'):
            self._tesseract_checked = True
            try:
                if TESSERACT_AVAILABLE and pytesseract and pytesseract.pytesseract.tesseract_cmd:
                    pytesseract.get_tesseract_version()
                    self.tesseract_available = True
                    print("✅ Tesseract disponível e configurado.")
                else:
                    self.tesseract_available = False
            except Exception as e:
                self.tesseract_available = False
                print(f"❌ Tesseract não disponível ou erro: {e}")
        return self.tesseract_available

    def canvasReleaseEvent(self, event):
        if not self.use_ocr:
            self._handle_manual_mode(event)
            return
        
        if not OPENCV_AVAILABLE:
            QMessageBox.critical(self.iface.mainWindow(), "Dependência Faltando", "❌ OpenCV não está disponível!")
            return

        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
        layer = self.iface.activeLayer()
        if layer is None:
            QMessageBox.warning(None, "Aviso", "Nenhuma camada ativa.")
            return

        x_m = round(point.x(), 2)
        y_m = round(point.y(), 2)
        print(f"\n🎯 Clique em coordenadas: X={x_m}, Y={y_m}")

        raster_path = layer.source()
        try:
            dataset = gdal.Open(raster_path, gdal.GA_ReadOnly)
            if dataset is None:
                QMessageBox.critical(None, "Erro", "Não foi possível abrir o raster com GDAL")
                return

            width, height, geotransform = dataset.RasterXSize, dataset.RasterYSize, dataset.GetGeoTransform()
            pixel_x = int((x_m - geotransform[0]) / geotransform[1])
            pixel_y = int((y_m - geotransform[3]) / geotransform[5])
            print(f"📍 Posição no pixel: X={pixel_x}, Y={pixel_y}")

            size = self.clip_size
            half = size // 2
            if not (half <= pixel_x < width - half and half <= pixel_y < height - half):
                self.iface.messageBar().pushWarning("Fora dos limites", "Ponto fora dos limites do raster.")
                return

            x_start, y_start = pixel_x - half, pixel_y - half
            img_bands = []
            for band_num in range(1, min(4, dataset.RasterCount + 1)):
                band = dataset.GetRasterBand(band_num)
                band_array = band.ReadAsArray(x_start, y_start, size, size)
                if band_array is not None:
                    img_bands.append(band_array)

            dataset = None
            if not img_bands:
                QMessageBox.critical(None, "Erro", "Não foi possível ler dados do raster")
                return

            img_data_raw = np.stack(img_bands, axis=-1) if len(img_bands) > 1 else img_bands[0]
            if len(img_data_raw.shape) == 3 and img_data_raw.shape[-1] >= 3:
                img_data_raw = img_data_raw[:, :, :3]

            if img_data_raw.dtype != np.uint8:
                img_min, img_max = img_data_raw.min(), img_data_raw.max()
                img_data_raw = ((img_data_raw - img_min) / (img_max - img_min) * 255).astype(np.uint8) if img_max > img_min else np.full_like(img_data_raw, 128, dtype=np.uint8)

            self._save_debug_data(img_data_raw, x_m, y_m, "gdal_raw")

        except Exception as e:
            QMessageBox.critical(None, "Erro GDAL", f"Erro ao processar com GDAL: {str(e)}")
            return
        
        self._start_ocr_with_progress(img_data_raw, x_m, y_m)

    def _handle_manual_mode(self, event):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
        x_m, y_m = round(point.x(), 2), round(point.y(), 2)
        print(f"\n✋ Modo Manual - Clique em coordenadas: X={x_m}, Y={y_m}")
        self._request_manual_depth_input(x_m, y_m)
    
    def _request_manual_depth_input(self, x_m, y_m):
        value, ok = QInputDialog.getDouble(
            self.iface.mainWindow(), "📝 Entrada Manual de Profundidade",
            f"📍 Coordenadas: X={x_m}, Y={y_m}\n\n🌊 Digite a profundidade (em metros):\n💡 Exemplo: 26.0 para 26 metros",
            0.0, 0.0, 999.9, 1)
        
        if ok and value > 0:
            profundidade_cm = int(value * 100)
            print(f"✅ Profundidade manual inserida: {value}m ({profundidade_cm}cm)")
            self._save_to_csv(x_m, y_m, profundidade_cm)
        else:
            self.iface.messageBar().pushMessage("Depth Reader OCR", "Entrada de dados cancelada.", level=Qgis.Info, duration=3)
    
    def _start_ocr_with_progress(self, img_data_raw, x_m, y_m):
        self.user_cancelled = False
        self.analysis_completed = False
        
        self.progress_dialog = QProgressDialog("🔍 Preparando análise OCR...", "❌ Cancelar", 0, 100, self.iface.mainWindow())
        self.progress_dialog.setWindowTitle("🤖 Depth Reader OCR - Analisando Batimetria")
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setMinimumWidth(400)
        self.progress_dialog.canceled.connect(self._cancel_ocr)
        
        # SUGESTÃO: Preparação para Parâmetros Configuráveis
        # Passa os parâmetros para a thread
        self.worker_thread = OCRWorkerThread(self, img_data_raw, x_m, y_m, self.rotations, self.preprocess_methods)
        self.worker_thread.progress_update.connect(self._update_progress)
        self.worker_thread.result_ready.connect(self._handle_ocr_result)
        self.worker_thread.error_occurred.connect(self._handle_ocr_error)
        self.worker_thread.finished.connect(self._cleanup_progress_safe)
        
        self.worker_thread.start()
        self.progress_dialog.show()
    
    def _update_progress(self, message, progress):
        if self.progress_dialog:
            self.progress_dialog.setLabelText(message)
            self.progress_dialog.setValue(progress)
            QApplication.processEvents()
    
    def _cancel_ocr(self):
        print("🚫 Usuário solicitou cancelamento da análise OCR")
        self.user_cancelled = True
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def _handle_ocr_result(self, profundidade_cm, x_m, y_m):
        print(f"📊 Resultado OCR recebido: {profundidade_cm}cm para coordenadas ({x_m}, {y_m})")
        self.analysis_completed = True
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if profundidade_cm == self.OCR_FAILED:
            reply = QMessageBox.question(
                self.iface.mainWindow(), "❌ OCR - Falha na Detecção",
                f"❌ Não foi possível detectar profundidade automaticamente em:\n📍 Coordenadas: X={x_m}, Y={y_m}\n\n🤔 Deseja inserir a profundidade manualmente?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self._request_manual_depth_input(x_m, y_m)
            else:
                self.iface.messageBar().pushMessage("Depth Reader OCR", "Ponto ignorado. Clique em outro local.", level=Qgis.Info, duration=4)
        else:
            profundidade_m = profundidade_cm / 100
            depth_display = f"{profundidade_m:.1f}m"
            # SUGESTÃO: Aqui seria o local para chamar um diálogo customizado
            # que permitiria a correção direta do valor.
            reply = QMessageBox.question(
                self.iface.mainWindow(), "🤖 Profundidade Detectada",
                f"🤖 O Depth Reader detectou:\n\n🌊 Profundidade: {depth_display}\n📍 Coordenadas: X={x_m}, Y={y_m}\n\n❓ A detecção está correta?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self._save_to_csv(x_m, y_m, profundidade_cm)
            else:
                self._request_manual_depth_input(x_m, y_m)
    
    def _handle_ocr_error(self, error_message):
        print(f"❌ Erro no processamento OCR: {error_message}")
        self.analysis_completed = True
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        QMessageBox.critical(
            self.iface.mainWindow(), "❌ Erro no Processamento OCR",
            f"❌ Erro durante a análise:\n\n{error_message}")
    
    def _cleanup_progress_safe(self):
        print("🧹 Limpando recursos da thread...")
        if self.progress_dialog and not self.analysis_completed and not self.user_cancelled:
            self.progress_dialog.close()
        self.progress_dialog = None
        self.worker_thread = None
        self.user_cancelled = False
        self.analysis_completed = False
        print("✅ Limpeza de recursos concluída")

    def _preprocess_clahe(self, img):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)

    def _preprocess_adaptive_threshold(self, img, method, block_size, C):
        binary = cv2.adaptiveThreshold(img, 255, method, cv2.THRESH_BINARY_INV, block_size, C)
        kernel = np.ones((2, 2), np.uint8)
        return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    def _perform_ocr_easyocr(self, img):
        results = []
        if self.easyocr_reader is not None:
            try:
                ocr_results = self.easyocr_reader.readtext(img, detail=True, allowlist='0123456789', width_ths=0.001, height_ths=0.001, paragraph=False, min_size=5)
                for (bbox, text, confidence) in ocr_results:
                    cleaned_text = re.sub(r'[^\d]', '', str(text))
                    if cleaned_text and confidence > 0.5:
                        results.append((cleaned_text, "easyocr", confidence))
            except Exception as e:
                print(f"❌ Erro EasyOCR: {e}")
        return results

    def _perform_ocr_tesseract(self, img):
        results = []
        if self.tesseract_available and PIL_AVAILABLE:
            try:
                pil_img = Image.fromarray(img)
                tess_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
                data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT, config=tess_config)
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    conf = int(data['conf'][i])
                    cleaned_text = re.sub(r'[^\d]', '', str(text))
                    if cleaned_text and conf > 50:
                        results.append((cleaned_text, "tesseract", conf / 100.0))
            except Exception as e:
                print(f"❌ Erro Tesseract: {e}")
        return results

    def _process_all_results(self, candidates):
        valid_results = []
        for text, method, angle, pp_method, ocr_confidence, text_len in candidates:
            numbers_only = re.sub(r'[^\d]', '', str(text))
            if not numbers_only or not (1 <= len(numbers_only) <= 3):
                continue

            try:
                value = int(numbers_only)
                if 1 <= value <= 999:
                    # SUGESTÃO: Usar constantes para o algoritmo de scoring.
                    final_score = ocr_confidence
                    if value in self.common_depths:
                        final_score *= self.COMMON_DEPTH_BONUS
                    else:
                        final_score *= self.UNCOMMON_DEPTH_PENALTY
                    final_score += (len(numbers_only) * self.TEXT_LENGTH_BONUS_FACTOR)
                    
                    valid_results.append((value, final_score, method, angle, pp_method, ocr_confidence, len(numbers_only)))
                    print(f"📊 Candidato: {value}m (Score Final: {final_score:.2f}, OCR Conf: {ocr_confidence:.2f}, Len: {len(numbers_only)})")
            except ValueError:
                pass

        if not valid_results:
            return self.OCR_FAILED

        valid_results.sort(key=lambda x: x[1], reverse=True)
        best_value = valid_results[0][0]
        return int(best_value * 100)

    def _save_debug_data(self, data, x_m, y_m, suffix):
        try:
            debug_dir = self.debug_dir
            os.makedirs(debug_dir, exist_ok=True)
            img_to_save = data if len(data.shape) == 3 else data
            if img_to_save.dtype != np.uint8:
                img_min, img_max = img_to_save.min(), img_to_save.max()
                img_to_save = ((img_to_save - img_min) / (img_max - img_min) * 255).astype(np.uint8) if img_max > img_min else np.full_like(img_to_save, 128, dtype=np.uint8)
            
            filename = f"{suffix}_{x_m}_{y_m}.png"
            filepath = os.path.join(debug_dir, filename)
            cv2.imwrite(filepath, img_to_save)
            print(f"💾 Debug salvo: {filepath}")
        except Exception as e:
            print(f"❌ Erro ao salvar debug: {e}")

    def _save_to_csv(self, x_m, y_m, profundidade_cm):
        try:
            csv_path = self.csv_path
            write_header = not os.path.exists(csv_path)
            with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if write_header:
                    writer.writerow(['X_m', 'Y_m', 'Profundidade_cm', 'Profundidade_m'])
                profundidade_m = profundidade_cm / 100 if profundidade_cm != self.OCR_FAILED else self.OCR_FAILED
                writer.writerow([x_m, y_m, profundidade_cm, profundidade_m])
            
            depth_display = f"{profundidade_m:.1f}m"
            message = f"✅ Profundidade salva: {depth_display} em ({x_m}, {y_m})"
            self.iface.messageBar().pushMessage("Depth Reader OCR", message, level=Qgis.Success, duration=5)
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), "❌ Erro ao Salvar", f"❌ Erro ao salvar dados:\n\n{str(e)}")