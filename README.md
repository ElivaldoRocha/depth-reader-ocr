# Depth Reader OCR

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green.svg)](https://plugins.qgis.org/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Plugin QGIS para extração automática de valores de profundidade de cartas náuticas raster brasileiras usando OCR (Reconhecimento Óptico de Caracteres).

![Demonstração do Plugin](https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=Plugin+em+A%C3%A7%C3%A3o)

## 🌊 Funcionalidades

- **OCR Avançado**: Utiliza OpenCV, Tesseract e EasyOCR para máxima precisão
- **Multi-rotacional**: Analisa texto em 13 ângulos diferentes (-90° a +270°)
- **Filtros Adaptativos**: Múltiplos algoritmos de pré-processamento
- **Interface Intuitiva**: Barra de progresso com possibilidade de cancelamento
- **Instalação Automática**: Gerencia dependências automaticamente
- **Compatibilidade Total**: Funciona com cartas GeoTIFF da Marinha do Brasil

## 📋 Requisitos

### Dependências Python
- `opencv-python>=4.5.0` - Processamento de imagem
- `pytesseract>=0.3.8` - OCR Tesseract
- `easyocr>=1.6.0` - OCR alternativo
- `pillow>=8.0.0` - Manipulação de imagens

### Engine OCR Externa
- **Tesseract OCR** (recomendado para melhor precisão)

## 🚀 Instalação

### Do Repositório Oficial QGIS
1. Abrir QGIS
2. Ir para **Plugins → Gerenciar e Instalar Plugins**
3. Buscar por **"Depth Reader OCR"**
4. Clicar em **Instalar**

### Instalação Manual
1. Baixar o arquivo ZIP do plugin
2. Extrair para o diretório de plugins do QGIS:
   ```
   Windows: C:\Users\{username}\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
   Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
   macOS: ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
   ```
3. Reiniciar QGIS
4. Ativar o plugin em **Plugins → Gerenciar e Instalar Plugins**

## ⚙️ Instalação de Dependências

### Automática
O plugin tentará instalar as dependências automaticamente na primeira execução.

### Manual (Recomendado)
Se a instalação automática falhar:

1. **Abrir Console Python do QGIS** (Plugins → Console Python)
2. **Executar comandos**:
   ```python
   import subprocess
   subprocess.check_call(['pip', 'install', 'opencv-python', 'pytesseract', 'easyocr', 'pillow'])
   ```

### Instalar Tesseract Engine (Recomendado)

#### **Windows:**

**Método 1 - Instalador Oficial:**
1. Baixar o instalador de [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Executar o instalador como administrador
3. **Importante**: Anotar o diretório de instalação (geralmente `C:\Program Files\Tesseract-OCR`)

**Método 2 - Configuração Manual do PATH (Recomendado):**

Como o instalador nem sempre adiciona automaticamente ao PATH do sistema, siga estes passos:

1. **Abrir Configurações do Sistema:**
   - Pressionar `Win + R`, digitar `sysdm.cpl` e pressionar Enter
   - OU ir em Painel de Controle → Sistema → Configurações avançadas do sistema

2. **Acessar Variáveis de Ambiente:**
   - Clicar em **"Variáveis de Ambiente..."**

3. **Editar a variável PATH:**
   - Na seção **"Variáveis do sistema"**, localizar e selecionar **"Path"**
   - Clicar em **"Editar..."**
   - Clicar em **"Novo"**
   - Adicionar o caminho completo do Tesseract: `C:\Program Files\Tesseract-OCR`
   - Clicar em **"OK"** em todas as janelas

4. **Verificar instalação:**
   - Abrir um novo **Prompt de Comando** (cmd)
   - Digitar: `tesseract --version`
   - Se aparecer a versão do Tesseract, a instalação foi bem-sucedida

**Método 3 - Configuração Específica no Plugin:**

Se preferir não alterar o PATH do sistema:

1. **Localizar o executável do Tesseract:**
   - Caminho padrão: `C:\Program Files\Tesseract-OCR\tesseract.exe`

2. **Configurar no código Python (se necessário):**
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr

# Verificar instalação
tesseract --version
```

**Para idiomas específicos:**
```bash
# Instalar pacotes de idiomas (opcional)
sudo apt-get install tesseract-ocr-por  # Português
sudo apt-get install tesseract-ocr-eng  # Inglês (geralmente já incluído)
```

#### **macOS:**

**Com Homebrew:**
```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Tesseract
brew install tesseract

# Verificar instalação
tesseract --version
```

**Com MacPorts:**
```bash
sudo port install tesseract
```

## 📊 Dados Compatíveis

### Cartas Náuticas Raster
- **Formato**: GeoTIFF
- **Fonte**: Marinha do Brasil (DHN/CHM)
- **Download gratuito**: [https://www.marinha.mil.br/chm/dados-do-segnav/cartas-raster](https://www.marinha.mil.br/chm/dados-do-segnav/cartas-raster)

⚠️ **Importante**: As cartas são disponibilizadas para fins acadêmicos e **não devem ser utilizadas para navegação**.

## 🎯 Como Usar

1. **Carregar carta náutica** raster no QGIS
2. **Ativar a ferramenta** clicando no ícone do plugin na barra de ferramentas
3. **Configurar parâmetros**:
   - Diretório para imagens de debug
   - Arquivo CSV de saída
   - Tamanho do recorte (padrão: 96px)
4. **Clicar nos pontos** onde deseja extrair profundidades
5. **Aguardar processamento** (barra de progresso mostrará o andamento)
6. **Resultados salvos** automaticamente no CSV especificado

### Configurações Avançadas
- **Tamanho do recorte**: Área analisada ao redor do clique (16-96 pixels)
- **Diretório de debug**: Salva imagens processadas para análise
- **Arquivo CSV**: Coordenadas e profundidades detectadas

## 🔧 Solução de Problemas

### "ModuleNotFoundError: No module named 'cv2'"
```python
# No Console Python do QGIS
import subprocess
subprocess.check_call(['pip', 'install', 'opencv-python'])
```

### "TesseractNotFoundError"

**Solução 1 - Verificar PATH:**
1. Abrir Prompt de Comando/Terminal
2. Digitar: `tesseract --version`
3. Se não funcionar, seguir os passos de configuração manual do PATH acima

**Solução 2 - Configuração direta no código:**
```python
# No Console Python do QGIS, configurar caminho manualmente
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux
# pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # macOS com Homebrew
```

**Solução 3 - Reinstalação:**
1. Desinstalar Tesseract completamente
2. Reinstalar seguindo os passos detalhados acima
3. Reiniciar o computador após a instalação

### "EasyOCR initialization failed"
- Verificar conexão com internet (EasyOCR baixa modelos automaticamente)
- Aguardar alguns minutos na primeira execução

### "Falha na instalação automática de dependências"
- Usar instalação manual das dependências
- Para ambientes corporativos: `pip install --user nome_do_pacote`
- Configurar proxy se necessário: `pip install --proxy http://proxy:porta nome_do_pacote`

### Plugin não aparece na barra de ferramentas
1. Verificar se está ativado em **Plugins → Gerenciar e Instalar Plugins**
2. Procurar por erros no **Console Python do QGIS**
3. Reinstalar dependências se necessário

### Problemas específicos do Tesseract no Windows
1. **Antivírus bloqueando**: Adicionar exceção para a pasta do Tesseract
2. **Permissões**: Executar QGIS como administrador temporariamente
3. **Espaços no caminho**: Evitar instalar em pastas com espaços ou caracteres especiais
4. **Versões conflitantes**: Desinstalar versões antigas antes de instalar nova

## 📈 Características Técnicas

- **Algoritmos OCR**: Tesseract PSM 6, EasyOCR com configurações otimizadas
- **Pré-processamento**: CLAHE, limiarização adaptativa, operações morfológicas
- **Multi-threading**: Processamento em background com feedback visual
- **Sistema de scoring**: Seleção inteligente baseada em confiança e contexto
- **Tratamento de erros**: Gracioso com mensagens informativas

## 📝 Licença

Este projeto está licenciado sob a **GNU General Public License v2.0** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Elivaldo Rocha**
- Email: carvalhovaldo09@gmail.com
- GitHub: [@elivaldorocha](https://github.com/elivaldorocha)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fazer fork do projeto
2. Criar branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para o branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 🐛 Reportar Problemas

Encontrou um bug? [Abra uma issue](https://github.com/elivaldorocha/depth-reader-ocr/issues) descrevendo:
- Versão do QGIS
- Sistema operacional
- Passos para reproduzir o problema
- Mensagens de erro (se houver)

## 📚 Documentação Adicional

- [Manual do Usuário](docs/manual-usuario.md)
- [Guia de Desenvolvimento](docs/desenvolvimento.md)
- [API Reference](docs/api.md)

## 🏆 Agradecimentos

- **Marinha do Brasil** pelo fornecimento gratuito das cartas náuticas
- **Comunidade QGIS** pelo excelente framework
- **Desenvolvedores** do OpenCV, Tesseract e EasyOCR
- **Grupo "Minicurso Eventos Extremos"** - Comunidade de aprendizado e troca de conhecimentos mantido pelo **Prof. Dr. Joaquim Carlos Barbosa Queiroz**

---

⭐ **Se este plugin foi útil, considere dar uma estrela no repositório!**
