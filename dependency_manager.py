# -*- coding: utf-8 -*-
"""
Gerenciador de Dependências para o plugin Depth Reader OCR
Verifica e instala automaticamente as bibliotecas necessárias
"""

import subprocess
import sys
import os
from qgis.PyQt.QtWidgets import QMessageBox, QProgressDialog, QApplication
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsMessageLog, Qgis

class DependencyChecker:
    """Verifica e instala dependências necessárias para o plugin"""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.required_packages = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow', 
            'pytesseract': 'pytesseract',
            'easyocr': 'easyocr'
        }
        
    def check_dependencies(self):
        """
        Verifica quais dependências estão disponíveis e quais estão faltando
        Retorna: (missing_packages, available_packages)
        """
        missing = []
        available = []
        
        for import_name, package_name in self.required_packages.items():
            try:
                if import_name == 'cv2':
                    import cv2
                elif import_name == 'PIL':
                    from PIL import Image
                elif import_name == 'pytesseract':
                    import pytesseract
                elif import_name == 'easyocr':
                    import easyocr
                    
                available.append(import_name)
                QgsMessageLog.logMessage(f"✅ {import_name} disponível", "DepthReaderOCR", Qgis.Info)
                
            except ImportError as e:
                missing.append((import_name, package_name))
                QgsMessageLog.logMessage(f"❌ {import_name} não encontrado: {e}", "DepthReaderOCR", Qgis.Warning)
        
        return missing, available
    
    def has_minimum_requirements(self):
        """Verifica se pelo menos os requisitos mínimos estão atendidos"""
        missing, available = self.check_dependencies()
        
        # OpenCV é obrigatório
        opencv_ok = 'cv2' in available
        
        # Pelo menos um OCR deve estar disponível
        ocr_ok = ('pytesseract' in available) or ('easyocr' in available)
        
        return opencv_ok and ocr_ok, missing
    
    def prompt_installation(self, missing_packages):
        """Pergunta ao usuário se quer instalar as dependências"""
        if not missing_packages:
            return True
            
        missing_names = [f"• {name} ({pkg})" for name, pkg in missing_packages]
        message = (
            "🔧 O plugin Depth Reader OCR precisa instalar algumas bibliotecas Python:\n\n"
            + "\n".join(missing_names) + "\n\n"
            "💡 Deseja instalá-las automaticamente?\n\n"
            "⏱️ Isto pode levar alguns minutos\n"
            "🌐 Requer conexão com internet\n"
            "💾 Serão instaladas no seu ambiente Python do QGIS"
        )
        
        reply = QMessageBox.question(
            self.parent,
            "Instalação de Dependências - Depth Reader OCR",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        return reply == QMessageBox.Yes
    
    def install_packages(self, packages_to_install):
        """Instala os pacotes necessários com barra de progresso"""
        if not packages_to_install:
            return True
            
        # Encontra o Python do QGIS
        python_exe = sys.executable
        
        # Cria diálogo de progresso
        progress = QProgressDialog(
            "Preparando instalação...", 
            "Cancelar", 
            0, 
            len(packages_to_install), 
            self.parent
        )
        progress.setWindowTitle("Depth Reader OCR - Instalando Dependências")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        QApplication.processEvents()  # Atualiza a interface
        
        success_count = 0
        failed_packages = []
        
        for i, (import_name, package_name) in enumerate(packages_to_install):
            if progress.wasCanceled():
                QMessageBox.information(
                    self.parent,
                    "Instalação Cancelada",
                    f"Instalação cancelada pelo usuário.\n"
                    f"Instalados: {success_count}/{len(packages_to_install)} pacotes"
                )
                return False
                
            progress.setLabelText(f"📦 Instalando {package_name}...\n({i+1}/{len(packages_to_install)})")
            progress.setValue(i)
            QApplication.processEvents()
            
            try:
                # Comando de instalação
                cmd = [python_exe, "-m", "pip", "install", package_name, "--user", "--no-warn-script-location"]
                
                QgsMessageLog.logMessage(f"Executando: {' '.join(cmd)}", "DepthReaderOCR", Qgis.Info)
                
                # Executa a instalação
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos timeout
                )
                
                if result.returncode == 0:
                    success_count += 1
                    QgsMessageLog.logMessage(f"✅ {package_name} instalado com sucesso", "DepthReaderOCR", Qgis.Success)
                else:
                    failed_packages.append((package_name, result.stderr))
                    QgsMessageLog.logMessage(f"❌ Erro ao instalar {package_name}: {result.stderr}", "DepthReaderOCR", Qgis.Critical)
                    
            except subprocess.TimeoutExpired:
                failed_packages.append((package_name, "Timeout - instalação demorou muito"))
                QgsMessageLog.logMessage(f"❌ Timeout ao instalar {package_name}", "DepthReaderOCR", Qgis.Critical)
                
            except Exception as e:
                failed_packages.append((package_name, str(e)))
                QgsMessageLog.logMessage(f"❌ Erro inesperado ao instalar {package_name}: {e}", "DepthReaderOCR", Qgis.Critical)
                
        progress.setValue(len(packages_to_install))
        progress.close()
        
        # Relatório final
        if success_count == len(packages_to_install):
            QMessageBox.information(
                self.parent,
                "✅ Instalação Concluída!",
                f"Todas as {success_count} dependências foram instaladas com sucesso!\n\n"
                "🔄 IMPORTANTE: Reinicie o QGIS para que as mudanças tenham efeito.\n\n"
                "🎉 Após reiniciar, o plugin estará pronto para uso!"
            )
            return True
            
        elif success_count > 0:
            failed_list = "\n".join([f"• {pkg}: {err[:100]}..." for pkg, err in failed_packages])
            QMessageBox.warning(
                self.parent,
                "⚠️ Instalação Parcial",
                f"Resultado da instalação:\n"
                f"✅ Instalados: {success_count}/{len(packages_to_install)}\n"
                f"❌ Falharam: {len(failed_packages)}\n\n"
                f"Pacotes que falharam:\n{failed_list}\n\n"
                "💡 Tente instalar manualmente os que falharam."
            )
            return False
            
        else:
            QMessageBox.critical(
                self.parent,
                "❌ Instalação Falhou",
                "Nenhum pacote pôde ser instalado automaticamente.\n\n"
                "💡 Tente a instalação manual:\n"
                "1. Abra o Prompt de Comando/Terminal\n"
                "2. Execute: pip install opencv-python pytesseract easyocr Pillow\n\n"
                "📋 Consulte o log do QGIS para mais detalhes."
            )
            return False
    
    def get_manual_instructions(self, missing_packages):
        """Retorna instruções para instalação manual"""
        if not missing_packages:
            return "Todas as dependências estão instaladas!"
            
        package_names = [pkg for _, pkg in missing_packages]
        cmd = f"pip install {' '.join(package_names)}"
        
        instructions = (
            "📋 INSTALAÇÃO MANUAL:\n\n"
            "1️⃣ Abra o Prompt de Comando (Windows) ou Terminal (Linux/Mac)\n\n"
            "2️⃣ Execute o comando:\n"
            f"   {cmd}\n\n"
            "3️⃣ Aguarde a instalação terminar\n\n"
            "4️⃣ Reinicie o QGIS\n\n"
            "5️⃣ Tente usar o plugin novamente"
        )
        
        return instructions