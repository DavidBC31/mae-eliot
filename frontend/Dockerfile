# Frontend Dockerfile
FROM node:18 as build

WORKDIR /app

# Copier package.json
COPY package.json ./

# Copier yarn.lock si présent, sinon on le générera
COPY yarn.loc[k] ./ 2>/dev/null || true

# Installer les dépendances (génère yarn.lock si absent)
RUN yarn install

# Copier le reste du code
COPY . .

# Build l'application
RUN yarn build

# Stage de production avec nginx
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=build /app/build /usr/share/nginx/html

# Copier la configuration nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]