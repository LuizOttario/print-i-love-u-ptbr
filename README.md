# Print I Love U — Tradução PT-BR (português do Brasil)

Tradução não oficial, feita por fã, do jogo **Print I Love U** (Steam) para **português do Brasil**,
com **acentos completos, inclusive ã e õ**.

O jogo não tem opção de português. Por isso, esta tradução **substitui os textos em inglês**:
deixe o jogo em **English** e ele vai aparecer em PT-BR.

Este repositório **não contém arquivos do jogo**. Os scripts editam os arquivos da sua própria
cópia e fazem backup antes.

## Como instalar

Você precisa do **Python 3** com **numpy** (`pip install numpy`).

1. Baixe este repositório (botão **Code → Download ZIP**) e extraia.
2. Ache a pasta do jogo: na Steam, clique com o botão direito no jogo → **Gerenciar → Procurar arquivos locais**.
3. Feche o jogo e rode, de dentro da pasta deste repositório:

```bash
python3 fonte_ptbr.py "CAMINHO/DO/JOGO"
```

Isso adiciona `ã õ Ã Õ` às fontes do jogo (leva 1 ou 2 minutos) e cria `data.win.bak`.

4. Faça backup do `languages.json` do jogo com o nome `languages.json.bak` e instale a tradução:

```bash
python3 apply.py "CAMINHO/DO/JOGO/languages.json.bak" "CAMINHO/DO/JOGO/languages.json"
```

Se aparecer `OK`, está pronto.

Exemplos de caminho:
- Linux: `~/.local/share/Steam/steamapps/common/Print I Love U`
- Windows: `C:\Program Files (x86)\Steam\steamapps\common\Print I Love U` (use `python` em vez de `python3`)

### Sem mexer nas fontes

O passo 3 é opcional. Sem ele, as fontes originais não têm `ã` nem `õ`, e o jogo apagaria essas
letras ("NÃO" viraria "NO"). Por isso o `apply.py` percebe sozinho se a fonte foi corrigida e, se
não foi, troca `ã`→`a` e `õ`→`o`. Pra forçar um modo, acrescente `com-til` ou `sem-til` no final
do comando.

### Como a fonte é corrigida

As duas fontes desenhadas do jogo têm as letras `ë ï Ë Ï`, que nenhum idioma do jogo usa. O
`fonte_ptbr.py` troca essas quatro por `ã õ Ã Õ` e desenha as novas a partir das próprias letras
do jogo (`â ô Â Ô` com o til do `ñ`). O resto do jogo não muda.

A janela da lixeira usa outra fonte, que ainda não tem `ã`/`õ` (nem `â`, `Ç`, `Ú`).

### Desinstalar

Copie `data.win.bak` de volta para `data.win` e `languages.json.bak` para `languages.json`, ou use
na Steam **Propriedades → Arquivos instalados → Verificar integridade**. A Steam também volta os
arquivos originais quando o jogo atualiza. Se isso acontecer, é só rodar os dois comandos de novo.

## Arquivos

- `pt.py` — todos os textos traduzidos
- `apply.py` — aplica a tradução no `languages.json` do jogo e valida o resultado
- `fonte_ptbr.py` — adiciona `ã õ Ã Õ` às fontes, no `data.win` do jogo

Print I Love U pertence aos seus criadores. Este é um projeto de fã, sem fins lucrativos.
