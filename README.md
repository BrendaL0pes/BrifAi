# Briefy
# Projeto Prático #01: Sistema de Briefings Personalizados

## Descrição do Projeto
Este projeto consiste em um sistema automatizado para a geração e distribuição de briefings de notícias personalizados. Desenvolvido em Python e orquestrado através do framework de agentes de IA Agno, o sistema permite que os usuários configurem suas preferências de conteúdo via Discord. Diariamente, de forma agendada, o sistema coleta notícias recentes, consolida as informações utilizando inteligência artificial e distribui o briefing final tanto no canal do Discord configurado quanto via e-mail.

Este projeto foi desenvolvido como requisito acadêmico para o curso de Engenharia de Software da Universidade Federal do Pampa (UNIPAMPA), com foco rigoroso em boas práticas de programação e arquitetura limpa.

## Requisitos Funcionais Implementados
1. **Coleta de Preferências (Discord):** Agente interativo para captura de tópicos, palavras-chave, limite de notícias, e-mail e ID do canal.
2. **Busca Automatizada:** Integração com motores de busca para recuperação de notícias recentes com base nos parâmetros do usuário.
3. **Geração de Conteúdo:** Consolidação e formatação do briefing estruturado utilizando o framework Agno.
4. **Distribuição Agendada (Discord):** Envio automático da mensagem para o servidor correspondente no horário estipulado.
5. **Distribuição via E-mail:** Disparo do briefing consolidado para o endereço de e-mail cadastrado.

## Práticas de Engenharia de Software e Arquitetura

O sistema foi projetado sob rigorosos padrões de qualidade, garantindo manutenibilidade e escalabilidade:

* **Clean Code:** Código redigido integralmente em inglês, seguindo as diretrizes da PEP8. Variáveis, classes e funções possuem nomenclaturas descritivas. Tipagem estática (Type Hints) e docstrings foram aplicadas em todas as assinaturas.
* **Limite de Complexidade:** Nenhuma função ou método do domínio da aplicação excede o limite estrito de 20 linhas de código.
* **S.O.L.I.D. Principles:**
  * **SRP (Single Responsibility Principle):** Serviços de e-mail, discord, busca de notícias e orquestração do agente estão isolados em suas respectivas classes.
  * **OCP (Open/Closed Principle):** O sistema permite a adição de novos provedores de notícias ou métodos de notificação sem a necessidade de alterar a lógica principal.
  * **ISP (Interface Segregation Principle):** Utilização de Classes Base Abstratas (ABCs) granulares.
  * **DIP (Dependency Inversion Principle):** Os módulos de alto nível dependem exclusivamente de interfaces abstratas (ex: `INewsFetcher`, `IEmailSender`), com as implementações concretas injetadas em tempo de execução.

## Estrutura de Diretórios

