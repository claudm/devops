## Análise do Comando

Vamos analisar este comando:

kubectl get deployment -o json | jq -r '.items[] | .metadata.labels | to_entries | map(.key + "_" + .value) | join("-") as $filename | . as $deployment | $filename, $deployment | @sh "echo \(.[$filename]) > \(.[$deployment] | tojson)" | xargs -I{} bash -c {}
- **kubectl get deployment -o json**: Esta parte do comando obtém os dados em formato JSON dos deployments usando o `kubectl`.

- **jq -r '.items[] | .metadata.labels | to_entries | map(.key + "_" + .value) | join("-") as $filename | . as $deployment | $filename, $deployment | @sh "echo \(.[$filename]) > \(.[$deployment] | tojson)"  | xargs -I{} bash -c {}'**: Este comando `jq` processa os dados JSON da seguinte forma:

    - `.items[]`: Itera sobre cada deployment.
    - `.metadata.labels | to_entries`: Converte o objeto de labels em um array de pares chave-valor.
    - `map(.key + "_" + .value)`: Mapeia cada par chave-valor para uma string no formato "chave_valor".
    - `join("-") as $filename`: Une as strings chave-valor com hífens para criar o nome do arquivo.
    - `. as $deployment`: Salva o objeto de deployment atual.
    - `$filename, $deployment`: Gera a saída com o nome do arquivo e o objeto de deployment juntos.
    - `@sh "echo \(.[$filename]) > \(.[$deployment] | tojson)"`: Usa `@sh` para executar um comando shell que imprime o JSON do deployment em um arquivo com o nome especificado.

- **xargs -I{} bash -c {}**: Esta parte do comando executa cada comando shell gerado pelo `jq`, criando efetivamente arquivos JSON individuais com base nas labels de cada deployment.

Este comando dividirá os deployments em arquivos JSON separados, com nomes baseados nas labels de cada deployment.

