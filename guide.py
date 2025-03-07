import os
import anthropic
import logging
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exclusion list
EXCLUSION_LIST = [
    '.git',
    '.venv',
    'node_modules',
    '__pycache__',
    '.DS_Store',
    'pb_data',
    'pb_public',
    'migrations',
    '.idea',
    'k8s',
    'olt',
    'venv',
    'compose.yaml',
    'Dockerfile',
    'handlers/__pycache__',
    'handlers/coralReefClustering/__pycache__',
    'handlers/disjointPathPlot/__pycache__'
    'handlers/logical_adjacency/__pycache__',
    'utils/__pycache__',
    'images',
    'data'
]

class ProjectAnalyzer:
    def __init__(self, project_dir):
        # Base directories
        self.project_dir = Path(project_dir)
        self.script_dir = Path(__file__).parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories
        self.findings_dir = self.script_dir / 'findings' / self.timestamp
        self.findings_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up file paths
        self.findings_path = self.findings_dir / 'findings.json'
        self.initial_summaries_path = self.script_dir / f'initial-summaries_{self.timestamp}.txt'
        
        # Initialize anthropic client
        self.client = anthropic.Anthropic()
        
        # Initialize findings file
        self._init_findings_file()
        
        logging.info(f"Initialized ProjectAnalyzer:")
        logging.info(f"- Project directory: {self.project_dir}")
        logging.info(f"- Script directory: {self.script_dir}")
        logging.info(f"- Findings directory: {self.findings_dir}")
        logging.info(f"- Initial summaries: {self.initial_summaries_path}")
        logging.info(f"- Findings JSON: {self.findings_path}")

    def _init_findings_file(self):
        """Initialize the findings JSON file with basic structure"""
        initial_structure = {
            'root_summary': '',
            'directories': {},
            'files': {}
        }
        self._write_findings(initial_structure)

    def _write_findings(self, data):
        """Write or update findings JSON file"""
        with open(self.findings_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _append_to_summaries(self, content):
        """Append content to the initial summaries file"""
        with open(self.initial_summaries_path, 'a') as f:
            f.write(f"{content}\n\n")

    def _read_findings(self):
        """Read current findings from JSON file"""
        with open(self.findings_path, 'r') as f:
            return json.load(f)

    def _update_findings(self, key, value):
        """Update specific section in findings"""
        findings = self._read_findings()
        if isinstance(key, tuple):  # For nested updates
            current = findings
            for k in key[:-1]:
                current = current.setdefault(k, {})
            current[key[-1]] = value
        else:
            findings[key] = value
        self._write_findings(findings)

    def is_excluded(self, path):
        return any(excluded in str(path) for excluded in EXCLUSION_LIST)

    def analyze_root(self):
        logging.info("Analyzing root directory...")
        root_contents = [str(f.relative_to(self.project_dir)) for f in Path(self.project_dir).rglob('*') 
                        if not self.is_excluded(f)]
        root_contents_str = '\n'.join(root_contents)

        message = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8192,
            temperature=0,
            system="Você é um assistente de IA que resume a linguagem principal, assim como o propósito de um projeto.",
            messages=[{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": f"Project directory: {self.project_dir}\n\nFiles and directories:\n{root_contents_str}\n\n"
                    "Com base na estrutura de diretórios e nomes de arquivos, qual é o idioma principal usado neste projeto?"
                    "Qual é o propósito do projeto? Forneça um resumo abrangente em uma linguagem acessível para desenvolvedores. O resumo deve ser gerado em Português do Brasil."
                }]
            }]
        )

        summary = message.content[0].text
        self._update_findings('root_summary', summary)
        self._append_to_summaries(f"Overview do projeto:\n{summary}")
        logging.info("Root analysis complete")

    def analyze_file(self, file_path):
        rel_path = str(Path(file_path).relative_to(self.project_dir))
        logging.info(f"Analyzing file: {rel_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            message = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=8192,
                temperature=0,
                system="Você é um assistente de IA que analisa arquivos de código-fonte.",
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"Analise este arquivo: {rel_path}\n\nContent:\n{content}\n\n"
                        "Por favor, providencie as informações abaixo:\n"
                        "1. Objetivo geral do arquivo\n"
                        "2. Lista de todos os campos/variáveis e suas finalidades\n"
                        "3. Definições de funções com entradas, saídas e propósitos\n"
                        "4. Quaisquer estruturas/classes e seu significado\n"
                        "5. Como este arquivo se encaixa no projeto\n"
                        "Todas as informações devem ser geradas em Português do Brasil."
                    }]
                }]
            )

            summary = message.content[0].text
            self._update_findings(('files', rel_path), summary)
            self._append_to_summaries(f"File: {rel_path}\n{summary}")
            logging.info(f"Completed analysis of file: {rel_path}")
            return summary

        except Exception as e:
            logging.error(f"Error analyzing file {file_path}: {str(e)}")
            return None

    def analyze_directory(self, dir_path):
        if self.is_excluded(dir_path):
            return

        rel_path = str(Path(dir_path).relative_to(self.project_dir))
        logging.info(f"Analyzing directory: {rel_path}")

        try:
            # Get list of files in directory
            files = [f for f in Path(dir_path).iterdir() 
                    if f.is_file() and not self.is_excluded(f)]

            if not files:  # Skip empty directories
                return

            # Analyze each file first
            file_summaries = []
            for file in files:
                summary = self.analyze_file(str(file))
                if summary:
                    file_summaries.append(f"{file.name}: {summary}")

            # Analyze directory as a whole
            if file_summaries:
                message = self.client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=8192,
                    temperature=0,
                    system="Você é um assistente de IA que analisa diretórios de código.",
                    messages=[{
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": f"Analise este diretório: {rel_path}\n\nFiles:\n{''.join(file_summaries)}\n\n"
                            "Forneça um resumo do propósito deste diretório e como seu conteúdo funciona em conjunto.\n"
                            "O resumo deve ser gerado em Português do Brasil."
                        }]
                    }]
                )

                summary = message.content[0].text
                self._update_findings(('directories', rel_path), summary)
                self._append_to_summaries(f"Directory: {rel_path}\n{summary}")
                logging.info(f"Completed analysis of directory: {rel_path}")

        except Exception as e:
            logging.error(f"Error analyzing directory {dir_path}: {str(e)}")

    def analyze_project(self):
        """First phase: analyze the project and collect initial summaries"""
        logging.info(f"Starting analysis of project: {self.project_dir}")
        
        # Analyze root first
        self.analyze_root()
        
        # Recursively analyze directories and files
        for root, dirs, files in os.walk(self.project_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self.is_excluded(d)]
            
            # Analyze current directory
            self.analyze_directory(root)

        logging.info("Project analysis complete")
        return self.initial_summaries_path, self.findings_path

    def generate_developer_guide(self):
        """Second phase: generate a well-organized developer guide in markdown"""
        logging.info("Generating developer guide...")
        
        # Read the collected data
        with open(self.findings_path, 'r') as f:
            findings = json.load(f)
        
        with open(self.initial_summaries_path, 'r') as f:
            initial_summaries = f.read()

        # Generate the final guidebook
        guidebook_content = self._create_markdown_guide(findings, initial_summaries)
        
        # Write the final guidebook
        guidebook_path = self.script_dir / f'guidebook_{self.timestamp}.md'
        with open(guidebook_path, 'w', encoding='utf-8') as f:
            f.write(guidebook_content)
        
        return guidebook_path

    def _create_markdown_guide(self, findings, initial_summaries):
        """Create the markdown developer guide using collected data"""
        
        message = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8192,
            temperature=0,
            system="Você é um escritor técnico especialista que cria guias para desenvolvedores claros e bem organizados.",
            messages=[{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": f"""
Com base nos seguintes dados de análise de projeto, crie um guia abrangente para desenvolvedores em formato markdown.

Resumos Iniciais:
{initial_summaries}

Resultados detalhados:
{json.dumps(findings, indent=2)}

Crie um guia do desenvolvedor que inclua:

1. Resumo Executivo
   - Objetivo do projeto
   - Principais tecnologias
   - Principais características

2. Arquitetura do Projeto
   - Visão geral de alto nível
   - Componentes principais
   - Padrões de design usados
   - Fluxo de dados

3. Setup & Instalação
   - Pré-requisitos
   - Configuração do ambiente
   - Configuração do projeto

4. Organização do código
   - Estrutura de diretório
   - Arquivos-chave e seus propósitos
   - Módulos/pacotes importantes

5. Conceitos Básicos
   - Abstrações principais
   - Interfaces principais
   - Modelos de dados

6. Fluxo de trabalho de desenvolvimento
   - Construção
   - Teste
   - Implantação

7. Referência de API
   - Funções principais
   - Classes importantes
   - Interfaces públicas

8. Tarefas comuns
   - Fluxos de trabalho de exemplo
   - Exemplos de código
   - Melhores práticas

Torne o guia prático e fácil de seguir. Use títulos claros, exemplos de código onde for relevante e inclua quaisquer notas ou avisos importantes.
O documento deve ser gerado em Português do Brasil.
"""
                }]
            }]
        )

        return message.content[0].text

def main():
    project_directory = os.environ.get('GUIDE_TARGET_PROJECT_DIRECTORY')
    if not project_directory:
        logging.error("GUIDE_TARGET_PROJECT_DIRECTORY environment variable is not set.")
        return

    # Phase 1: Analyze project
    analyzer = ProjectAnalyzer(project_directory)
    initial_summaries_path, findings_path = analyzer.analyze_project()
    
    # Phase 2: Generate developer guide
    guidebook_path = analyzer.generate_developer_guide()

    logging.info(f"Guide generation complete. Results saved to:\n"
                f"Initial Summaries: {initial_summaries_path}\n"
                f"Findings: {findings_path}\n"
                f"Developer Guide: {guidebook_path}")

if __name__ == "__main__":
    main()


