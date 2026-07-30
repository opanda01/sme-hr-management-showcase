# GitHub repository About (kobik-myhr-system)

Use these values in **Settings → General → About** or via `gh repo edit`.

## Description (≤350 characters)

```
Kobik HR — full-stack SME HR platform (mobile + web + FastAPI). Public showcase; live previews at kobik.dev.
```

## Website

```
https://kobik.dev
```

## Topics

```
fastapi
postgresql
react-native
expo
react
vite
tailwindcss
hr-management
monorepo
docker
redis
typescript
human-resources
sme
```

## CLI (reference)

```bash
gh repo edit opanda01/kobik-myhr-system \
  --description "Kobik HR — full-stack SME HR platform (mobile + web + FastAPI). Public showcase; live previews at kobik.dev." \
  --homepage "https://kobik.dev"

gh api --method PUT repos/opanda01/kobik-myhr-system/topics \
  -f names='["fastapi","postgresql","react-native","expo","react","vite","tailwindcss","hr-management","monorepo","docker","redis","typescript","human-resources","sme"]'
```
