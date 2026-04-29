# Revisão das Tarefas do Plano Cirúrgico v1.3

## Objetivo

Revisar todas as 29 tarefas contra o código real para identificar:
1. Linhas incorretas ou desatualizadas
2. Problemas de IA (código macarrônico, padrões antipadrão)
3. Instruções ambíguas que geram código errado
4. Dependências implícitas não documentadas
5. Constraints que podem quebrar dados existentes

## Implementation Plan

- [ ] 1. Revisar Onda 1 (T-1.1 a T-1.11) contra models.py real
- [ ] 2. Revisar Onda 2 (T-2.1 a T-2.4) contra models.py real
- [ ] 3. Revisar Onda 3 (T-3.1 sinais) contra models.py real
- [ ] 4. Revisar Onda 4 (T-4.1 a T-4.7) contra models.py e views.py real
- [ ] 5. Revisar Onda 5 (T-5.1 a T-5.3) contra models.py real
- [ ] 6. Revisar Bonus (T-B.1) contra views.py real
- [ ] 7. Produzir documento com correções para cada tarefa
- [ ] 8. Aplicar correções nos arquivos markdown

## Verification Criteria

- Todas as linhas de referência batem com o código real
- Nenhum padrão antipadrão de IA nas instruções
- Todas as constraints têm instrução de data migration prévia
- Nenhum código "macarrônico" nas sugestões