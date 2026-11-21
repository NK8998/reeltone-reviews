FROM node:24-bookworm-slim AS source
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package*.json ./
RUN npm ci
COPY . .

FROM source AS development
RUN chown node:node /app
USER node
EXPOSE 3000
CMD ["node", "node_modules/next/dist/bin/next", "dev", "--turbopack", "--hostname", "0.0.0.0", "--port", "3000"]

FROM source AS build
ARG NEXT_PUBLIC_SITE_URL=https://reviews.reeltone.site
ENV NEXT_PUBLIC_SITE_URL=${NEXT_PUBLIC_SITE_URL}
RUN npm run build

FROM node:24-bookworm-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
