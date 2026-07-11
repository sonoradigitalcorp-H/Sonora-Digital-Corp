FROM twentycrm/twenty:latest

COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["node", "dist/main"]
