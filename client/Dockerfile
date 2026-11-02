FROM node:24.22.2-alpine3.24 AS deps
WORKDIR /app
ENV HUSKY=0 NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
RUN npm ci

FROM node:24.22.2-alpine3.24 AS build
WORKDIR /app
ENV HUSKY=0 NEXT_TELEMETRY_DISABLED=1
ARG TESSIO_SERVER_URL=http://api:8000
ENV TESSIO_SERVER_URL=$TESSIO_SERVER_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:24.22.2-alpine3.24 AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node", "server.js"]
