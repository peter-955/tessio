FROM node:24.22.2-alpine3.24
WORKDIR /app
COPY package.json ./
COPY *.ts ./
USER node
EXPOSE 3000
CMD ["node", "server.ts"]
