# build stage
FROM node:lts-alpine as build-stage

WORKDIR /home/app/frontend
COPY frontend/package.json /home/app/frontend
RUN npm cache verify
RUN npm install
COPY frontend /home/app/frontend
RUN npm run build


FROM nginx:stable-alpine as production-stage

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /home/app/frontend/dist /dist/

CMD ["nginx", "-g", "daemon off;"]