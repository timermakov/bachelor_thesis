FROM node:lts-alpine

WORKDIR /usr/src/frontend
COPY package*.json ./
RUN npm install
RUN npm install -g vite


COPY . .

# Use vite directly with host binding
CMD ["vite", "--host"]
