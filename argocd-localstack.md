
## Crossplane, Argo CD, and Localstack for local testing

![](https://cdn-images-1.medium.com/max/2048/0*Qpew1MeYDHgwGi4F)

In this article, we are going to explore how we can combine three powerful tools: [Crossplane](https://www.crossplane.io/), [Argo CD](https://argo-cd.readthedocs.io/), and [Localstack](https://www.localstack.cloud/), to create a simple, visually tangible, and cost-effective setup for learning and practicing. The aim of this document is not to provide an in-depth exploration of the technologies used here; instead, it focuses on the interaction among them and the synergy they create.

![](https://cdn-images-1.medium.com/max/2000/1*sRcPnjbqMyToL-PrPK2Ulw.png)

## First of all, let's get our setup in place.

✅ **A Git repo**

There’s not much to say here, just grab an empty repository to play with. We’ll be using it to store all our manifests.

✅ **Kubernetes**

As Minikube is one of the most extensively used tools for local clusters, let’s use it. If you’re not familiar with the installation process, you can find it [here](https://minikube.sigs.k8s.io/docs/start/)

✅ **Argo CD**

We will be using Argo CD to manage all other software components from now on, but before that, we need to install it. The documentation is excellent, a vanilla [installation](https://argo-cd.readthedocs.io/en/stable/getting_started/#1-install-argo-cd) is pretty simple and is more than enough for our current project. Just make sure to skip the core version, we need the UI.

    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

✅ **Oh, the repo!**

We almost forgot to configure our git repo into Argo CD. Assuming you’re utilizing a private repository for your tests, you can follow the instructions in the UI as outlined [here](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/). However, for this article, I’ll be using my public repository:

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

Once your repo is defined, you need to set up an Application to manage all the other applications that will be discovered from the repo (App of Apps).

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

## **Well, Crossplane or what?**

Now that we have our cluster up and running with Argo CD in place, we can deploy Localstack and Crossplane using Argo CD.

In the public repo, you can find a couple of Applications, which are organized this way for the sake of the article. However, you can group them more simply if you prefer.

* localstack

* crossplane

* crossplane-providers

* test-env

*In this section, we’re going to cheat a bit by leveraging [Argo CD Sync Phases and Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/) to ensure that components are deployed in a convenient sequence, helping us reduce friction.*

**Localstack and Crossplane**

Pretty simple here, we’re just deploying the official helm chart for both tools

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

**crossplane-providers**

Here’s something a bit different: we’re deploying [Crossplane Providers](https://docs.crossplane.io/latest/concepts/providers/) from manifests placed in a specific path. Our focus is on playing with Crossplane and AWS (through Localstack), so for now, we’re only installing the A[WS provider](https://marketplace.upbound.io/providers/upbound/provider-aws/v0.46.0). However, you can add anything else you need later on.

Keep in mind that the provider deployment can take a while, depending on your local setup, it will deploy a lot of CRDs.

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

ℹ️ Note that Crossplane Providers are installed in a second stage after getting ***crossplane*** Application up and running.

## **The glue**

By now, we have Localstack, Crossplane, and its AWS provider running. The next step is to stitch both together, providing us with the experience of interacting directly with AWS.

We have this simple secret that contains a dummy set of credentials

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

As you can see here, it grabs credentials from the previously defined Secret, and in the endpoint section, it points to our Localstack service.

## **Getting everything in motion!**

The last moving part here is our “hello world”, managed by the Application called **test-env**.
Similar to ***crossplane-providers**,* this Application will be searching for Crossplane manifests in a specific path, in this case, **/test-env**

Here, you’ll find a very simple AWS setup: a VPC, three subnets, a security group, and an EC2 instance.

Now it is time to sync up ***test-env*** Application

✨ At this point, everything comes together, and we can see the true potential of this setup. ✨

We can use the Argo CD UI to more easily visualize all the resources deployed by Crossplane. With version control in place, we have the flexibility to roll back changes if needed, along with all the cool features of GitOps.

![](https://cdn-images-1.medium.com/max/2000/1*cvohOMceyYPA9cJVXkrKaA.png)

![](https://cdn-images-1.medium.com/max/2000/1*n4DWv3CccRfxMsOHSLGhPg.png)

## Conclusion

In summary, our journey through Crossplane, Argo CD, and Localstack showcases a seamless, cost-effective local setup for experimenting with Crossplane and AWS. By leveraging the Argo CD UI and embracing GitOps practices, we highlight the powerful synergy of these tools.
