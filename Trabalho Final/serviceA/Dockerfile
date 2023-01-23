FROM node:16.11.1

RUN mkdir /app/

WORKDIR /app/

COPY ./ /app/
RUN rm -rf /app/package-lock.json
RUN npm install

EXPOSE 7001
EXPOSE 7002

CMD ["node", "index.js"]