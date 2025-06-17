# Interactive Story Generator

**Projeto Final CS50P**

## Sobre o Projeto

Este é um jogo de aventura interativa em texto onde podes navegar por histórias com escolhas que afetam o resultado. O projeto começou como uma brincadeira com amigos em português e agora foi traduzido para inglês com melhorias adicionais.

## Funcionalidades

- **3 Histórias Diferentes**: Castelo Encantado, Floresta Sombria e Estação Espacial
- **Sistema de Escolhas**: As tuas decisões mudam a história
- **Inventário**: Coleta e usa itens durante o jogo
- **Save/Load**: Grava o progresso em qualquer altura
- **Estatísticas**: Acompanha o tempo jogado e escolhas feitas
- **Interface Colorida**: Usa a biblioteca Rich para melhor apresentação

## Como Instalar

```bash
# Instalar dependências
pip install rich pytest

# Executar o jogo
python project.py

# Executar testes
pytest test_project.py
```

## Como Jogar

1. Executa `python project.py`
2. Escolhe uma história no menu principal
3. Seleciona as opções numeradas para avançar
4. Comandos especiais:
   - `I` - Ver inventário
   - `S` - Gravar jogo
   - `T` - Ver estatísticas
   - `Q` - Sair para o menu

## Estrutura do Projeto

```
project.py          # Ficheiro principal
test_project.py     # Testes
saves/              # Jogos gravados
stats/              # Estatísticas
```

## Tecnologias Usadas

- **Python 3.11+**
- **Rich** - Interface colorida
- **JSON** - Armazenamento de dados
- **Pytest** - Testes

## Desenvolvimento

Este projeto foi originalmente criado por diversão com amigos em português. Para o CS50, traduzi para inglês e adicionei várias melhorias como múltiplas histórias e sistema de estatísticas.

**Uso de IA**: Foi usada principalmente para ajudar com elementos visuais e formatação da interface, permitindo focar no desenvolvimento da lógica do jogo e arquitetura do código.

## Testes

O projeto inclui testes abrangentes que cobrem:
- Navegação entre cenas
- Sistema de save/load
- Cálculo de estatísticas
- Validação de entrada do utilizador

## Possíveis Melhorias

- Mais histórias e cenários
- Sistema de conquistas
- Editor de histórias
- Modo multiplayer