# Beleva local GitOps automation

## What runs where

| Layer | Tool | Responsibility |
| --- | --- | --- |
| Local cluster | kind + kubectl | Runs the Kubernetes nodes on the laptop. |
| Release packaging | Helm | Renders the single `helm/beleva-stack` application chart. |
| Continuous deployment | Argo CD | Watches `main` and syncs the Helm stack to kind. |
| Continuous integration | Jenkins | Tests, builds images, pushes Docker Hub images, and commits the image tag. |
| Monitoring | kube-prometheus-stack | Installs Prometheus and Grafana in `monitoring`. |

## Normal workflow

1. Make a code change.
2. Commit and push it to `main`.
3. GitHub notifies Jenkins.
4. Jenkins runs tests, builds `saarvi51/horizon-django` and `saarvi51/horizon-nginx`, and pushes the commit SHA tag to Docker Hub.
5. Jenkins commits that image tag to `helm/beleva-stack/values.yaml` with `[skip ci]`.
6. Argo CD detects the new commit and deploys release `beleva` into namespace `horizon`.

The desired daily commands are:

```bash
git add .
git commit -m "describe the change"
git push origin main
```

## One-time local bootstrap

Create a local `.env` from `.env.example`, fill in real values, and never commit it. Then run:

```bash
make bootstrap
make status
```

`make bootstrap` is idempotent: it reuses `beleva-cluster`, installs Argo CD and monitoring if missing, creates the Kubernetes secret from `.env`, and applies the Argo CD Application.

Ubuntu needs GNU Make for the short commands. Install it once if `make` is missing:

```bash
sudo apt-get update
sudo apt-get install -y make
```

## Useful commands

```bash
make help
make status
make app
make argocd
make grafana
make prometheus
make logs
make lint
make template
```

Port-forward commands keep running until `Ctrl+C`:

| Command | Browser URL |
| --- | --- |
| `make app` | http://localhost:8081 |
| `make argocd` | https://localhost:8082 |
| `make grafana` | http://localhost:3000 |
| `make prometheus` | http://localhost:9091 |

If a local port is busy, override it directly with `kubectl port-forward` using another port.

## Jenkins one-time configuration

1. Install Jenkins on the WSL host or run it with Docker, ensuring its agent can run `docker`, `docker compose`, and `git`.
2. Create a Pipeline or Multibranch Pipeline that checks out `main` from `https://github.com/saarvi35/horizon.git` and uses `jenkins/Jenkinsfile`.
3. Add Jenkins credentials:
   - `docker`: Docker Hub username/password credential using a Docker Hub access token.
   - `github-token`: secret-text GitHub fine-grained token with repository **Contents: Read and write** permission.
4. Configure the job to ignore Jenkins-created commits containing `[skip ci]`; otherwise the release-tag commit can trigger another build.
5. Add a GitHub webhook for `push` events. Because Jenkins runs on the laptop, expose it using a secure tunnel (Cloudflare Tunnel or ngrok) or use Jenkins SCM polling as a fallback.

## Important migration rule

Do not apply the old `kubernetes/` application manifests and the Argo CD application at the same time. They create separate application resources. The final GitOps owner is Argo CD release `beleva` from `helm/beleva-stack`.

Before the first final cutover, verify the new `beleva-*` pods and `beleva-nginx` service work. The new chart deliberately uses a separate `beleva-mysql` PVC, so it starts with a new local MySQL database. If the old MySQL data matters, export/import it before removing the older manual `horizon-*` resources.

## Troubleshooting a failed GitOps rollout

Always inspect the image and the previous container logs before changing the chart:

```bash
kubectl get deployment beleva-django -n horizon \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
kubectl logs -n horizon deployment/beleva-django --previous --tail=100
kubectl logs -n horizon deployment/beleva-nginx --previous --tail=100
```

If the rollout uses an old or invalid Docker Hub image, fix the source, commit and push `main`, then let Jenkins build and publish a fresh SHA-tagged image. Do not delete the stable older `horizon-*` application before the `beleva-*` pods are healthy.
