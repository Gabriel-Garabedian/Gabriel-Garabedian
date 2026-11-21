# Cartões do perfil

Identidade editorial inspirada na referência enviada: papel claro, texto escuro, Instrument Serif e Geist incorporadas em WOFF, azul/vermelho/amarelo. Conteúdo adaptado a Gabriel Garabedian. Retrato ASCII derivado do avatar público; nenhuma imagem do autor da referência foi copiada.

## Gerar

`python scripts/render_readme_cards.py` usa o JSON salvo. `python scripts/render_readme_cards.py --refresh` atualiza o calendário público antes de renderizar. Python 3.12, apenas biblioteca padrão na execução diária. As fontes já foram recortadas e estão em fonts/, com licenças OFL.

`STATIC=1 python scripts/render_readme_cards.py` gera o estado final sem animações (PowerShell: `$env:STATIC='1'`). Remova a variável e gere novamente antes de publicar. Todos os movimentos CSS são desligados por `prefers-reduced-motion: reduce`; SVGs não fazem chamadas externas nem executam JavaScript.

## Dados e atualização

O calendário público do GitHub é a fonte. O parser valida datas consecutivas e contagens, e falha sem sobrescrever o JSON anterior se o HTML mudar. Não revela repositórios privados. Meses nas extremidades podem estar parciais; o cartão mostra o intervalo exato. Sequência significa maior sequência dentro desse intervalo, não recorde histórico. A escala do gráfico azul é relativa ao dia de maior atividade.

O workflow existente snake.yml foi substituído pela geração dos cartões às 09:00 UTC (06:00 em São Paulo). A branch output antiga permanece intacta, mas a cobrinha não integra mais o README. GitHub pode atrasar cron e desativar agendas de repositórios públicos inativos; workflow_dispatch permite execução manual. Permissão contents:write é restrita ao workflow. Push concorrente na main faz o job falhar com segurança, sem force push; reexecute neste caso.

## Verificar

`python -m unittest discover -s scripts -p 'test_*.py'`

A atualização real pelo GitHub Actions depende da publicação deste pacote. Nenhum token pessoal é necessário. README contém links e descrições alternativas para acesso ao conteúdo sem imagens.
