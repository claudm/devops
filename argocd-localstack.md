
## Crossplane, Argo CD e Localstack para testes locais

![](https://cdn-images-1.medium.com/max/2048/0*Qpew1MeYDHgwGi4F)

Neste artigo, vamos explorar como podemos combinar três ferramentas poderosas: [Crossplane](https://www.crossplane.io/), [Argo CD](https://argo-cd.readthedocs.io/), e [Localstack](https://www.localstack.cloud/), ara criar uma configuração simples, visualmente tangível e econômica para aprender e praticar. O objetivo deste documento não é fornecer uma exploração aprofundada das tecnologias usadas aqui; em vez disso, ele se concentra na interação entre elas e na sinergia que elas criam.

![](https://cdn-images-1.medium.com/max/2000/1*sRcPnjbqMyToL-PrPK2Ulw.png)

## Primeiro, vamos preparar nossa configuração.

✅ **Um repositório Git**

Não há muito o que dizer aqui, apenas pegue um repositório vazio para brincar. Nós o usaremos para armazenar todos os nossos manifestos.

✅ **Kubernetes**

Como o rancher é uma das ferramentas mais amplamente utilizadas para clusters locais, vamos usá-lo. Se você não estiver familiarizado com o processo de instalação, você pode encontrá-lo [aqui](https://www.youtube.com/watch?v=suz9No_FHSo)

✅ **Argo CD**

Usaremos o Argo CD para gerenciar todos os outros componentes de software de agora em diante, mas antes disso, precisamos instalá-lo. A documentação é excelente, uma  [instalação](https://argo-cd.readthedocs.io/en/stable/getting_started/#1-install-argo-cd) vanilla é bem simples e é mais do que suficiente para nosso projeto atual. Apenas certifique-se de pular a versão principal, precisamos da UI.

    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

✅ **Ah, o repositório!**

Quase esquecemos de configurar nosso repositório git no Argo CD. Supondo que você esteja utilizando um repositório privado para seus testes, você pode seguir as instruções na UI conforme descrito  [aqui](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/). No entanto, para este artigo, usarei meu repositório público:

```
	cat <<EOF | kubectl apply -f -
    apiVersion: v1
    kind: Secret
    metadata:
      name: repo-demo
      namespace: argocd
      labels:
        argocd.argoproj.io/secret-type: repository
    stringData:
      type: git
      url: https://github.com/leunamnauj/Crossplane-Argocd-and-localstack-for-local-environments.git
EOF

```

Depois que seu repositório estiver definido, você precisará configurar um aplicativo para gerenciar todos os outros aplicativos que serão descobertos no repositório (App of Apps)..

```
	cat <<EOF | kubectl apply -f -
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: appofapps
      namespace: argocd
      finalizers:
        - resources-finalizer.argocd.argoproj.io
      labels:
        name: appofapps
    spec:
      project: default
      source:
        repoURL: https://github.com/leunamnauj/Crossplane-Argocd-and-localstack-for-local-environments.git
        targetRevision: HEAD
        path: .
    
      destination:
        server: https://kubernetes.default.svc
        namespace: argocd
      syncPolicy:
        automated:
          prune: true 
          selfHeal: true 
          allowEmpty: true
        syncOptions:
        - CreateNamespace=true
      revisionHistoryLimit: 10
EOF

```

## **Bem, Crossplane ou o quê?**

Agora que nosso cluster está instalado e funcionando com o Argo CD, podemos implantar o Localstack e o Crossplane usando o Argo CD.

No repositório público, você pode encontrar alguns Applications, que são organizados dessa forma para o bem do artigo. No entanto, você pode agrupá-los de forma mais simples, se preferir..

* localstack

* crossplane

* crossplane-providers

* test-env

*Nesta seção, vamos trapacear um pouco aproveitando [as fases e ondas do Argo CD Sync](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/) para garantir que os componentes sejam implantados em uma sequência conveniente, o que nos ajuda a reduzir o atrito.*

**Localstack e Crossplane**

Bem simples aqui, estamos apenas implantando o gráfico oficial do leme para ambas as ferramentas

```
	cat <<EOF | kubectl apply -f -
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: localstack
      namespace: argocd
      labels:
        name: localstack
      annotations:
        argocd.argoproj.io/hook: Sync
        argocd.argoproj.io/sync-wave: "1"
        argocd.argoproj.io/hook-delete-policy: HookFailed
      finalizers:
        - resources-finalizer.argocd.argoproj.io
    spec:
      project: default
      source:
        repoURL: https://localstack.github.io/helm-charts
        targetRevision: "0.6.5"
        chart: localstack
      destination:
        server: https://kubernetes.default.svc
        namespace: localstack
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
          allowEmpty: true
        syncOptions:
        - CreateNamespace=true
      revisionHistoryLimit: 10
EOF

```


```
	cat <<EOF | kubectl apply -f -
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: crossplane
      namespace: argocd
      labels:
        name: crossplane
      annotations:
        argocd.argoproj.io/hook: Sync
        argocd.argoproj.io/sync-wave: "1"
        argocd.argoproj.io/hook-delete-policy: HookFailed
      finalizers:
        - resources-finalizer.argocd.argoproj.io
    spec:
      project: default
      source:
        repoURL: https://charts.crossplane.io/stable 
        targetRevision: "1.14.5"
        chart: crossplane  
      destination:
        server: https://kubernetes.default.svc
        namespace: crossplane-system
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
          allowEmpty: true
        syncOptions:
        - CreateNamespace=true
      revisionHistoryLimit: 10
EOF

```

**provedores de crossplane**

Aqui está algo um pouco diferente: estamos implantando [Crossplane Providers](https://docs.crossplane.io/latest/concepts/providers/) a partir de manifestos colocados em um caminho específico. Nosso foco é brincar com Crossplane e AWS (por meio do Localstack), então, por enquanto, estamos instalando apenas o  A[AWS provider](https://marketplace.upbound.io/providers/upbound/provider-aws/v0.46.0). No entanto, você pode adicionar qualquer outra coisa que precisar mais tarde.

Tenha em mente que a implantação do provedor pode demorar um pouco, dependendo da sua configuração local, ele implantará muitos CRDs.

```
	cat <<EOF | kubectl apply -f -
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: crossplane-providers
      namespace: argocd
      labels:
        name: crossplane
      annotations:
        argocd.argoproj.io/hook: Sync
        argocd.argoproj.io/sync-wave: "2"
        argocd.argoproj.io/hook-delete-policy: HookFailed
      finalizers:
        - resources-finalizer.argocd.argoproj.io
    spec:
      project: default
      source:
        repoURL: git@github.com:leunamnauj/Crossplane-Argocd-and-localstack-for-local-environments.git
        targetRevision: HEAD
        path: crossplane-providers
      destination:
        server: https://kubernetes.default.svc
        namespace: crossplane-system
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
          allowEmpty: true
        syncOptions:
        - CreateNamespace=true
      revisionHistoryLimit: 10

EOF
```

ℹ️ Observe que os provedores Crossplane são instalados em um segundo estágio após o aplicativo ***crossplane*** estar instalado e funcionando.

## **O glue**

Agora, temos o Localstack, o Crossplane e seu provedor AWS em execução. O próximo passo é unir os dois, nos dando a experiência de interagir diretamente com a AWS.

Temos este secrets simples que contém um conjunto fictício de credenciais

```
	cat <<EOF | kubectl apply -f -
    apiVersion: v1
    kind: Secret
    metadata:
      name: localstack-aws-secret
      namespace: crossplane-system
      annotations:
        argocd.argoproj.io/hook: Sync
        argocd.argoproj.io/sync-wave: "3"
        argocd.argoproj.io/hook-delete-policy: HookFailed
    type: Opaque
    data:
      creds: W2RlZmF1bHRdCmF3c19hY2Nlc3Nfa2V5X2lkID0gdGVzdAphd3Nfc2VjcmV0X2FjY2Vzc19rZXkgPSB0ZXN0Cg==
	EOF
And a [ProviderConfig](https://docs.crossplane.io/latest/concepts/providers/#configure-a-provider)
	cat <<EOF | kubectl apply -f -
    apiVersion: aws.upbound.io/v1beta1
    kind: ProviderConfig
    metadata:
      name: localstack
      annotations:
        argocd.argoproj.io/hook: Sync
        argocd.argoproj.io/sync-wave: "3"
        argocd.argoproj.io/hook-delete-policy: HookFailed
    spec:
      credentials:
        source: Secret
        secretRef:
          name: localstack-aws-secret
          namespace: crossplane-system
          key: creds
      endpoint:
        hostnameImmutable: true
        url:
          type: Static
          static: http://localstack.localstack.svc.cluster.local:4566
EOF
```

Como você pode ver aqui, ele pega credenciais do Segredo definido anteriormente e, na seção de endpoint, aponta para nosso serviço Localstack.

## **Colocando tudo em movimento!**

A última parte móvel aqui é o nosso “hello world”, gerenciado pelo aplicativo chamado  **test-env**.
Semelhante ao  ***crossplane-providers***,  este aplicativo estará procurando por manifestos Crossplane em um caminho específico, neste caso, **/test-env**

Aqui, você encontrará uma configuração muito simples da AWS: uma VPC, três sub-redes, um grupo de segurança e uma instância EC2

Agora é hora de sincronizar o aplicativo ***test-env***  

✨ Neste ponto, tudo se encaixa e podemos ver o verdadeiro potencial desta configuração.. ✨

Podemos usar a Argo CD UI para visualizar mais facilmente todos os recursos implantados pelo Crossplane. Com o controle de versão em vigor, temos a flexibilidade de reverter as alterações, se necessário, junto com todos os recursos interessantes do GitOps.

![](https://cdn-images-1.medium.com/max/2000/1*cvohOMceyYPA9cJVXkrKaA.png)

![](https://cdn-images-1.medium.com/max/2000/1*n4DWv3CccRfxMsOHSLGhPg.png)

## Conclusion

Em resumo, nossa jornada pelo Crossplane, Argo CD e Localstack mostra uma configuração local perfeita e econômica para experimentar o Crossplane e o AWS. Ao alavancar a IU do Argo CD e adotar as práticas do GitOps, destacamos a poderosa sinergia dessas ferramentas.

## instalando o traefik para ajudar a acessar os endereços do argocd 

```
helm upgrade --install traefik traefik/traefik -n traefik-v2 --create-namespace\
  --set dashboard.enabled=true \
  --set ports.web.port=8000 \
  --set ports.websecure.port=8443 \
  --set ports.traefik.port=9000 \
  --set ports.traefik.expose.default=true \
  --set service.type=LoadBalancer \
  --set additionalArguments[0]="--api.dashboard=true" \
  --set additionalArguments[1]="--api.insecure=true" \
  --set ingressRoute.dashboard.enabled=true \
  --set ingressRoute.dashboard.entryPoints[0]=web 

```
```
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: traefik-dashboard-ingress
  namespace: traefik-v2
  annotations:
    kubernetes.io/ingress.class: traefik    
    traefik.ingress.kubernetes.io/router.entrypoints: web       
spec:
  rules:
  - host: traefik.localhost
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: traefik
            port:
              number: 9000
EOF

```
