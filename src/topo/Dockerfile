######### Npm part #########
FROM node:14.21.3 AS StaticBuilding

ARG APP_VERSION=ce
ARG NODE_ENV=production
ENV NPM_VERSION 6.14.15

# install requirements & build
COPY . /package_vue
WORKDIR /package_vue

ENV BK_OAUTH2_TOKEN=${BK_OAUTH2_TOKEN}
ENV BKPAAS_ENVIRONMENT=${BKPAAS_ENVIRONMENT}

RUN npm install --unsafe-perm --registry=https://mirrors.tencent.com/npm/
RUN npm run build
ENTRYPOINT ["npm", "run", "server"]
