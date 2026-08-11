# PRODUCT.md

## Product

**Merkaz** is a shared file library for Merkaz Tze'irim (Kfar Kama). Members sign in to browse and download shared files, upload content for review, and send suggestions. Admins approve users and uploads, manage roles, and export activity logs.

## Users

- **Member:** browse/download files, upload for approval, track own uploads, reset password, use useful links / bug report.
- **Admin:** all member tasks, plus create folders, search, delete/edit paths, approve/deny users and uploads, download metrics logs.

## Surfaces (client)

| Route | Purpose |
|-------|---------|
| `/login`, `/register`, `/forgot-password`, `/reset-password` | Auth |
| `/dashboard` | File browser |
| `/dashboard/upload` | Upload files (optional `?path=`) |
| `/dashboard/my-uploads` | Upload history |
| `/metrics`, `/users`, `/pending`, `/denied`, `/uploads` | Admin dashboard tabs |

## Brand

- Logo: mustard brushstroke + Hebrew מרכז צעירים + "K Φ A P - K A M A"
- Assets: `client/public/assets/icons/banner-logo.webp`, `banner-logo-dark-mode.webp`
- Visual system of record: root `DESIGN.md`

## Mode

All product UI is **Operate**: task completion, scanability, and consistent chrome over marketing expression.

## Out of scope (current)

- Challenge / puzzle / leaderboard shell (removed from React shell unless re-requested)
- Marketing landing page

## Stack

- Frontend: React + Vite (`client/`)
- Backend: Flask (`server/`)
- Auth: session cookies + JWT bearer
