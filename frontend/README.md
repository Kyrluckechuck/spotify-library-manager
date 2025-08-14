# Spotify Library Manager – Frontend

This is the React + TypeScript + Vite frontend for Spotify Library Manager. It talks to the GraphQL API at `/graphql` and uses Apollo Client and TanStack Router.

## Development

- Start via the repo root: `make dev` (runs API, worker, and Vite dev server)
- Or only the frontend:
  ```bash
  cd frontend
  yarn install --frozen-lockfile
  yarn dev
  ```

The dev server proxies `/graphql` to `http://localhost:5000`.

## Scripts

- `yarn lint` – ESLint (zero warnings enforced)
- `yarn test:run` – unit tests
- `yarn generate` – GraphQL codegen (`codegen.yml`)
- `yarn build` – typecheck + Vite build

## Notes

- GraphQL schema URL is configured via `codegen.yml` using `VITE_API_URL`.
- Only `frontend/yarn.lock` is tracked. npm lockfiles are ignored.
