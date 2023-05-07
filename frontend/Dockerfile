FROM node:18-alpine
LABEL maintainer="Cato Yeung"

WORKDIR /app

COPY ./frontend/package.json ./
RUN npm install

COPY ./ ./

RUN npm run build # will build remix app
ENV NODE_ENV=development

CMD ["npm", "run" ,"dev"]