FROM nginx:stable-alpine

# Удаляем дефолтный index
RUN rm -rf /usr/share/nginx/html/*

COPY ./default.conf /etc/nginx/conf.d/default.conf

# Копируем dist
COPY dist/ /usr/share/nginx/html/

# Копируем свой конфиг (опционально)
# COPY nginx.conf /etc/nginx/conf.d/default.conf