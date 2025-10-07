FROM golang:1.20-alpine AS builder; WORKDIR /app; COPY go.mod go.sum ./; RUN go mod download; COPY . .; RUN go build -o /app/main ./cmd/{{ project_name }};
FROM alpine:latest; COPY --from=builder /app/main /app/main; ENTRYPOINT [ "/app/main" ]
