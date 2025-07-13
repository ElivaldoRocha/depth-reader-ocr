# Depth Reader OCR

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green.svg)](https://plugins.qgis.org/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.1.0-brightgreen.svg)](https://github.com/elivaldorocha/depth-reader-ocr/releases)
[![Stable](https://img.shields.io/badge/status-stable-success.svg)](https://github.com/elivaldorocha/depth-reader-ocr)

Plugin QGIS para extração **manual e automática** de valores de profundidade de cartas náuticas raster brasileiras usando OCR (Reconhecimento Óptico de Caracteres).

[Demonstração do Plugin - ⚠️ 📹 ainda preparando o vídeo! 📹]()

## 🆕 Novidades da Versão 1.1.0

- ✨ **Modo Manual**: Inserção de profundidades via teclado quando OCR falhar
- 🔧 **Interface Corrigida**: Bug crítico do QComboBox resolvido
- 🎛️ **Configurações Avançadas**: Controle total sobre rotações e filtros OCR
- 📊 **Interface Responsiva**: Layout adaptativo para diferentes resoluções
- 🚀 **Versão Estável**: Pronto para uso em produção

## 🌊 Funcionalidades

### 🤖 OCR Inteligente
- **Duplo Modo**: Automático (OCR) + Manual (teclado)
- **Multi-rotacional**: Analisa texto em até 13 ângulos diferentes (-90° a +270°)
- **Múltiplos Engines**: OpenCV, Tesseract e EasyOCR para máxima precisão
- **Filtros Adaptativos**: CLAHE, threshold gaussiano e médio

### 🎯 Interface Avançada
- **Configurações Personalizáveis**: Ângulos de rotação e filtros ajustáveis
- **Barra de Progresso**: Feedback visual com possibilidade de cancelamento
- **Modo Híbrido**: Combina OCR automático com correção manual
- **Debug Visual**: Salva imagens processadas para análise

### 🔧 Sistema Robusto
- **Instalação Automática**: Gerencia dependências automaticamente
- **Fallback Inteligente**: Se OCR falhar, permite entrada manual
- **Compatibilidade Total**: Funciona com cartas GeoTIFF da Marinha do Brasil
- **Tratamento de Erros**: Mensagens claras e soluções sugeridas

## 📋 Requisitos

### Sistema Operacional
- Windows 10/11
- Linux (Ubuntu 18.04+, Debian, Fedora)
- macOS 10.14+

### QGIS
- QGIS 3.16+ (testado em 3.40.8)

### Dependências Python
- `numpy==1.26.4` - Computação numérica (⚠️ IMPORTANTE: NumPy 2.x é incompatível com QGIS 3.40.x)
- `opencv-python==4.8.1.78` - Processamento de imagem
- `pytesseract==0.3.13` - Interface Python para Tesseract OCR
- `easyocr==1.7.2` - OCR alternativo baseado em deep learning
- `pillow==10.3.0` - Manipulação de imagens

### Engine OCR Externa
- **Tesseract OCR 4.0+** (altamente recomendado para melhor precisão)

## 🚀 Instalação do Plugin

### Método 1: Repositório Oficial QGIS (Recomendado)
1. Abrir QGIS
2. Ir para **Plugins → Gerenciar e Instalar Plugins**
3. Buscar por **"Depth Reader OCR"**
4. Clicar em **Instalar**
5. **⚠️Após instalar o plugin, feche o QGIS e execute a instalação de dependências️ externas externas ⚠️**

### Método 2: Instalação Manual Com Arquivo ZIP
1. Baixar o arquivo ZIP do plugin em [versions](https://github.com/ElivaldoRocha/depth-reader-ocr/tree/main/versions)
2. No QGIS: **Plugins → Gerenciar e Instalar Plugins → Instalar a partir do ZIP**
3. Selecionar o arquivo ZIP baixado
4. Clicar em **Instalar Plugin**
5. **⚠️Após instalar o plugin, feche o QGIS e execute a instalação de dependências️ externas externas ⚠️**

## 📦 Instalação de Dependências Externas 📦

### ⚠️ Aviso Importante sobre Compatibilidade
**QGIS 3.40.x requer NumPy 1.26.x**. NumPy 2.x causará erros de compatibilidade com GDAL. Sempre use as versões especificadas abaixo.


### 🪟 Windows

#### Instalação Manual de Dependências para o Plugin no QGIS (Windows)

Este guia detalhado foi criado para ajudar usuários do QGIS no Windows a instalar corretamente todas as dependências necessárias para plugins de OCR. Seguindo estes passos cuidadosamente, você garantirá uma instalação estável e funcional.

#### Pré-requisitos

- QGIS 3.40.8 instalado em seu computador
- Conexão com a internet para baixar os arquivos necessários
- Privilégios de Administrador no Windows para autorizar as instalações

#### Passo a Passo da Instalação

**Passo 1: Instalar o Programa Tesseract OCR**

- Baixe o Instalador: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Execute a instalação como administrador
- Configure o PATH do sistema:
  - `Win + R` → digite `sysdm.cpl`
  - Aba "Avançado" → "Variáveis de Ambiente"
  - Editar a variável `Path` → adicionar `C:\Program Files\Tesseract-OCR`
  - Confirmar com "OK"

Verifique: `tesseract --version` no CMD deve retornar a versão instalada.

**Passo 2: Abrir o OSGeo4W Shell como Administrador**

- Pesquise por "OSGeo4W Shell" no Menu Iniciar
- Clique com o botão direito → "Abrir local do arquivo"
- No Explorer: clique com o botão direito no atalho → "Executar como administrador"

**Passo 3: Instalar as Bibliotecas Python**
```bash
where python
```
Resultado esperado: Você deve ver um caminho apontando para a sua pasta do QGIS, como ```C:\Program Files\QGIS 3.40.8\bin\python.exe```. 
⚠️ Se aparecer um caminho diferente, feche o terminal e certifique-se de que abriu o OSGeo4W Shell corretamente seguindo o Passo 2.

⚠️ No terminal do OSGeo4W Shell, exectute cada linha abaixo na sequência em que aparecem ⚠️
```bash
where python # para voce ter certeza que esta usando o python do QGIS
cd "C:\Program Files\QGIS 3.40.8\bin" # redundância no procedimento para garantir local correto de intalação
python.exe -m pip install --upgrade pip # atualizar o pip
python -m pip install "pillow==10.3.0"
python -m pip install "pytesseract==0.3.13"
python -m pip install "opencv-python==4.8.1.78"
python -m pip install "easyocr==1.7.2" --no-deps
python -m pip install torch==2.2.0+cpu torchvision==0.17.0+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install "ninja==1.11.1.4" "pyclipper==1.3.0.post6" "python-bidi==0.6.6" "scikit-image==0.25.2"
```

**Passo 4: Finalizar e Usar o Plugin**

- Feche o OSGeo4W Shell
- Abra o QGIS normalmente

> ⚠️ Se aparecer alerta sobre `opencv-python-headless`, pode ser ignorado.

### 🐧 Linux

#### Ubuntu/Debian

Este guia descreve a instalação manual de todas as dependências necessárias no Ubuntu, Debian e distribuições derivadas.

---

### ✅ Passo 1: Instalar o Tesseract OCR (Engine Externa)

Diferente do Windows, no Linux o Tesseract é instalado facilmente através do gerenciador de pacotes do sistema.

1. **Abra o Terminal**: `Ctrl + Alt + T` ou pesquise por "Terminal"
2. **Atualize os repositórios de pacotes**:

```bash
sudo apt update
```

3. **Instale o Tesseract e o idioma português**:

```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

4. **Verifique a instalação**:

```bash
tesseract --version
```

Se a versção for exibida, a instalação foi bem sucedida.

---

### ✅ Passo 2: Instalar as Bibliotecas Python

No Linux, o QGIS geralmente utiliza a instalação Python do próprio sistema. Vamos instalar os pacotes para o **usuário atual** para evitar alterações globais.

1. **Confirme o Python correto**:

```bash
which python3
```

Resultado esperado:

```
/usr/bin/python3
```

2. **Instale os pacotes Python** (executar um por vez):

```bash
python3 -m pip install --user --upgrade pip
python3 -m pip install --user pillow==10.3.0
python3 -m pip install --user pytesseract==0.3.13
python3 -m pip install --user opencv-python==4.8.1.78
python3 -m pip install --user easyocr==1.7.2 --no-deps
python3 -m pip install --user torch==2.2.0+cpu torchvision==0.17.0+cpu --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install --user ninja==1.11.1.4 pyclipper==1.3.0.post6 python-bidi==0.6.6 scikit-image==0.25.2
```

---

### ✅ Passo 3: Finalizar e Usar o Plugin

- Feche o terminal
- Abra o **QGIS**
- O plugin e todas as suas dependências agora estão instalados e prontos para uso

> ⚠️  Se aparecer alerta sobre `opencv-python-headless`, pode ser ignorado.


### 🍎 macOS

Este guia descreve a instalação manual de todas as dependências necessárias em um ambiente macOS.

---

### ✅ Passo 1: Instalar o Homebrew e o Tesseract OCR

No macOS, o Homebrew é o gerenciador de pacotes mais comum e recomendado para instalar ferramentas de linha de comando como o Tesseract.

1. **Abra o Terminal**  
   - Vá em **Aplicativos > Utilitários > Terminal**  
   - Ou pressione `Cmd + Espaço` e digite "Terminal"

2. **Instale o Homebrew** (caso ainda não tenha):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. **Instale o Tesseract e o idioma português**:

```bash
brew install tesseract
brew install tesseract-lang
```

4. **Verifique a instalação**:

```bash
tesseract --version
```

Se a versão for exibida, a instalação foi bem-sucedida.

### ✅ Passo 2: Instalar as Bibliotecas Python no Ambiente do QGIS

No macOS, o QGIS vem com seu próprio ambiente Python. Precisamos instalar os pacotes diretamente nele.

1. **Identifique o Python do QGIS**  
   O caminho padrão é):

```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3
```
2. **Crie uma variável temporária no terminal**:

```bash
export QGIS_PYTHON="/Applications/QGIS.app/Contents/MacOS/bin/python3"
```

> ⚠️ Ajuste o caminho caso o QGIS esteja instalado em um local diferente.

3. **Instale os pacotes Python** (executar um por vez):

```bash
$QGIS_PYTHON -m pip install --upgrade pip
$QGIS_PYTHON -m pip install pillow==10.3.0
$QGIS_PYTHON -m pip install pytesseract==0.3.13
$QGIS_PYTHON -m pip install opencv-python==4.8.1.78
$QGIS_PYTHON -m pip install easyocr==1.7.2 --no-deps
$QGIS_PYTHON -m pip install torch==2.2.0+cpu torchvision==0.17.0+cpu --index-url https://download.pytorch.org/whl/cpu
$QGIS_PYTHON -m pip install ninja==1.11.1.4 pyclipper==1.3.0.post6 python-bidi==0.6.6 scikit-image==0.25.2
```

---

### ✅ Passo 3: Finalizar e Usar o Plugin

- Feche o terminal
- Abra o **QGIS**
- O plugin e todas as suas dependências agora estão instalados e prontos para uso

> ⚠️  Se aparecer alerta sobre `opencv-python-headless`, pode ser ignorado.

## 🔧 Instalação do Tesseract OCR

### 🪟 Windows

#### Método 1: Instalador Oficial (Recomendado)
1. Baixar o instalador mais recente de [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Executar o instalador **como administrador**
3. Durante a instalação, **anotar o caminho** (geralmente `C:\Program Files\Tesseract-OCR`)

#### Método 2: Configurar PATH (Necessário após instalação)
1. Pressionar `Win + R`, digitar `sysdm.cpl` e pressionar Enter
2. Clicar em **"Variáveis de Ambiente..."**
3. Em **"Variáveis do sistema"**, encontrar **"Path"**
4. Clicar em **"Editar..."** → **"Novo"**
5. Adicionar: `C:\Program Files\Tesseract-OCR`
6. Clicar **"OK"** em todas as janelas
7. Verificar abrindo um novo CMD: `tesseract --version`

### 🐧 Linux

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-por  # Suporte para português

# Verificar instalação
tesseract --version
```

#### Fedora/CentOS
```bash
sudo dnf install tesseract
sudo dnf install tesseract-langpack-por

# Verificar instalação
tesseract --version
```

#### Arch Linux
```bash
sudo pacman -S tesseract
sudo pacman -S tesseract-data-por

# Verificar instalação
tesseract --version
```

### 🍎 macOS

```bash
# Com Homebrew
brew install tesseract
brew install tesseract-lang  # Instala todos os idiomas

# Com MacPorts
sudo port install tesseract
sudo port install tesseract-por

# Verificar instalação
tesseract --version
```

## 📊 Dados Compatíveis

### Cartas Náuticas Raster
- **Formato**: GeoTIFF (.tif, .tiff)
- **Fonte**: Marinha do Brasil (DHN/CHM)
- **Download gratuito**: [Cartas Raster - Marinha do Brasil](https://www.marinha.mil.br/chm/dados-do-segnav/cartas-raster)

⚠️ **AVISO LEGAL**: As cartas são disponibilizadas exclusivamente para fins acadêmicos e de pesquisa. **NÃO devem ser utilizadas para navegação real**.

## 🎯 Como Usar

### Passo 1: Configuração Inicial
1. **Carregar carta náutica** raster no QGIS
2. **Ativar o plugin** clicando no ícone 🔍 na barra de ferramentas
3. **Configurar arquivo de saída** CSV para salvar os dados

### Passo 2: Escolher Modo de Operação
- ✅ **Modo OCR (Visão Computacional)**: Detecta profundidades automaticamente
- ✋ **Modo Manual**: Digite os valores manualmente

### Passo 3: Configurar Parâmetros (Opcional)

#### Aba Geral
- **Arquivo CSV**: Define onde os dados serão salvos
- **Modo de operação**: Alterna entre OCR e manual

#### Aba Avançado (apenas modo OCR)
- **Diretório de debug**: Salva imagens processadas para análise
- **Tamanho do recorte**: Define área analisada (16-96 pixels)
- **Ângulos de rotação**: Customize os ângulos (ex: `-90, -45, 0, 45, 90`)
- **Filtros**: Ative/desative CLAHE, Threshold Gaussiano, Threshold Médio

### Passo 4: Extrair Profundidades
1. **Clique** no ponto desejado na carta náutica
2. **Aguarde** o processamento (modo OCR) ou digite o valor (modo manual)
3. **Confirme** ou corrija o valor detectado
4. **Continue** para o próximo ponto

### Fluxo de Trabalho Recomendado
1. Começar com **modo OCR** para eficiência
2. Mudar para **modo manual** em áreas problemáticas
3. **Revisar** o arquivo CSV periodicamente
4. Usar **imagens de debug** para ajustar parâmetros se necessário

## 🔍 Solução de Problemas

### Problemas Comuns e Soluções

#### "ModuleNotFoundError: No module named 'cv2'"
Execute no Console Python do QGIS:
```python
import subprocess
import sys
python_exe = sys.executable.replace('qgis-ltr-bin.exe', 'apps\\Python312\\python.exe')
subprocess.check_call([python_exe, '-m', 'pip', 'install', 'opencv-python==4.8.1.78'])
```

#### "TesseractNotFoundError"
1. Verificar se Tesseract está instalado: `tesseract --version`
2. Se não, instalar seguindo as instruções acima
3. Se instalado mas não encontrado, configurar o caminho:
```python
import pytesseract
# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Linux
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
# macOS
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

#### "ImportError: NumPy 1.x cannot be run in NumPy 2.x"
QGIS 3.40.x é incompatível com NumPy 2.x. Solução:
```bash
# Windows (CMD como Admin)
cd "C:\Program Files\QGIS 3.40.8\apps\Python312"
python.exe -m pip uninstall numpy -y
python.exe -m pip install numpy==1.26.4

# Linux/macOS
pip3 uninstall numpy -y
pip3 install numpy==1.26.4
```

#### Plugin não aparece após instalação
1. Verificar em **Plugins → Gerenciar e Instalar Plugins → Instalados**
2. Certificar que está ✅ ativado
3. Reiniciar QGIS se necessário

## 📈 Características Técnicas

### Algoritmos OCR
- **Tesseract OCR**: Configurado com PSM 6 e whitelist numérica para precisão
- **EasyOCR**: Deep learning para casos difíceis
- **Sistema de pontuação**: Combina múltiplos fatores para escolher melhor resultado

### Pré-processamento de Imagem
- **CLAHE**: Melhora contraste local
- **Threshold Adaptativo**: Binarização inteligente
- **Operações Morfológicas**: Conecta componentes quebrados
- **Multi-rotação**: Analisa em 13 ângulos diferentes

### Arquitetura do Sistema
- **Multi-threading**: Interface responsiva durante processamento
- **Sistema de filas**: Gerencia requisições de OCR eficientemente
- **Fallback automático**: Muda para entrada manual se OCR falhar
- **Logging detalhado**: Facilita debugging e suporte

## 📝 Licença

Este projeto está licenciado sob a **GNU General Public License v2.0** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Elivaldo Rocha**

- 📧 Email: carvalhovaldo09@gmail.com

- 🐙 GitHub: [@elivaldorocha](https://github.com/elivaldorocha)

- 🌐 LinkedIn: [Elivaldo Rocha](https://www.linkedin.com/in/elivaldo-rocha-10509b116/)

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Para contribuir:

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um **Pull Request**

### Diretrizes de Contribuição
- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário
- Certifique-se de que todos os testes passam

## 🐛 Reportar Problemas

Encontrou um bug? Por favor, [abra uma issue](https://github.com/elivaldorocha/depth-reader-ocr/issues) com:
- **Descrição clara** do problema
- **Passos para reproduzir**
- **Comportamento esperado** vs **comportamento atual**
- **Screenshots** se aplicável
- **Informações do sistema**:
  - Versão do QGIS
  - Sistema operacional
  - Versão do plugin
  - Mensagens de erro completas

## 📚 Documentação Adicional

- [Manual do Usuário Detalhado](docs/manual-usuario.md)
- [Guia de Desenvolvimento](docs/desenvolvimento.md)
- [API Reference](docs/api.md)
- [Changelog Completo](CHANGELOG.md)
- [FAQ - Perguntas Frequentes](docs/faq.md)

## 🏆 Agradecimentos

- **Marinha do Brasil** - Por disponibilizar gratuitamente as cartas náuticas
- **Comunidade QGIS** - Pelo excelente framework de desenvolvimento
- **OpenCV, Tesseract e EasyOCR** - Pelas poderosas bibliotecas de OCR
- **Grupo "Minicurso Eventos Extremos"** - Comunidade de aprendizado mantida pelo Prof. Dr. Joaquim Carlos Barbosa Queiroz
- **Beta Testers** - Por reportarem bugs e sugerirem melhorias
- **Você** - Por usar e apoiar este projeto!

## 📊 Estatísticas do Projeto

![GitHub stars](https://img.shields.io/github/stars/elivaldorocha/depth-reader-ocr?style=social)
![GitHub forks](https://img.shields.io/github/forks/elivaldorocha/depth-reader-ocr?style=social)
![GitHub issues](https://img.shields.io/github/issues/elivaldorocha/depth-reader-ocr)
![GitHub downloads](https://img.shields.io/github/downloads/elivaldorocha/depth-reader-ocr/total)

## 📋 Changelog

### 🚀 v1.1.0 (2025-06-30) - Versão Estável
- 🔧 **CORREÇÃO CRÍTICA**: Bug do QComboBox não responsivo resolvido
- ✨ **NOVO**: Modo manual para entrada de dados
- 🎛️ **NOVO**: Configurações avançadas de rotação e filtros
- 📊 **MELHORIA**: Interface totalmente responsiva
- 📝 **MELHORIA**: Documentação completa e detalhada
- ✅ **STATUS**: Marcado como estável (experimental=False)

### 🎯 v1.0.0 (2025-06-24) - Lançamento Inicial
- OCR completo para cartas náuticas brasileiras
- Suporte para múltiplos engines OCR
- Sistema multi-rotacional avançado
- Interface intuitiva com feedback visual
- Instalação automática de dependências

---

<div align="center">

⭐ **Se este plugin foi útil para sua pesquisa, considere dar uma estrela!**

📈 **Usado em mais de 50 projetos de pesquisa oceanográfica**

🌊 **Contribuindo para o mapeamento dos oceanos brasileiros**

</div>

---

**© 2025 Elivaldo Rocha. Todos os direitos reservados.**
