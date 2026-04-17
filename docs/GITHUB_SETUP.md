# Publish To GitHub (Step-by-Step)

This guide publishes your local project to your GitHub account (`@Quiford`).

## 1. Create a repo on GitHub

1. Go to https://github.com/new
2. Repository name suggestion: `proxy-sorter`
3. Set visibility (Public recommended for stars/forks)
4. Do not add README/license from GitHub UI (already in your local project)
5. Click **Create repository**

## 2. Initialize git locally

Run in your project folder:

```bash
git init
git branch -M main
git add .
git commit -m "feat: initial release of Quiford Proxy Sorter"
```

## 3. Connect remote and push

Replace `<REPO_URL>` with your repo URL, for example:
`https://github.com/Quiford/proxy-sorter.git`

```bash
git remote add origin <REPO_URL>
git push -u origin main
```

## 4. Improve profile and repo trust

After push:

- Add repo topics: `python`, `cybersecurity`, `proxy`, `socks5`, `networking`, `automation`
- Pin this repo on your GitHub profile
- Add a short project description in repo settings
- Enable Issues and Discussions
- Enable branch protection once collaborators join

## 5. Add social proof

- Create a release tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

- Add a screenshot/GIF demo to README
- Keep a clear roadmap and changelog
- Respond fast to issues and pull requests
