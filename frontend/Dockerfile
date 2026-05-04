FROM node:20-alpine

WORKDIR /app

# Install dependencies based on the preferred package manager
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# Next.js telemetry disable
ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000

CMD ["npm", "run", "dev"]
