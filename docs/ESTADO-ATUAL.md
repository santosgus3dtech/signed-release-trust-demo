# Estado atual — Signed Release Trust Demo

Revisão documental: 13/10/2026. Nenhum material criptográfico gerado ou release instalado.

## Arquitetura observada

`trustdemo/release.py` contém construção de manifest, SHA-256, escrita assinada, `verify_release`, `install_release`, `active_version` e `rollback`. `trustdemo/lease.py` separa emissão e validação de lease vinculada a dispositivo, usando Ed25519. `pyproject.toml` declara cryptography, Python >=3.10 e comando `trust-demo`.

## Regras documentadas

[README](../README.md) descreve JSON canônico, verificação por tamanho/hash, rejeição de escapes de caminho, ativação atômica e checks de audiência/nonce/expiração. A demo usa aplicação fictícia e exclui materiais proprietários, contas e chaves de produção. Essas propriedades não foram certificadas por execução nesta sessão.

## Operação e testes

Tutorial apresenta `python -m trustdemo.cli keys`, `sign-release`, `verify-release` e `install`, com argumentos próprios do workspace de demo. Teste documentado: `pytest -q`; configuração aponta para `tests`. Todos não executados nesta tarefa. Não há chave ou workspace lido.

## Retomada

Sugestões: revisar a função de confiança afetada pela próxima mudança; escolher workspace sintético; executar testes pertinentes apenas com novo escopo. Não transportar esta implementação para produto real como aprovação de segurança. Não há decisões históricas novas inferidas.

[Índice](INDEX.md)
