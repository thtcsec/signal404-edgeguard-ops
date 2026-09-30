FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY Directory.Build.props ./
COPY shared/EdgeGuard.Shared/ shared/EdgeGuard.Shared/
COPY services/telemetry-api/ services/telemetry-api/
RUN dotnet publish services/telemetry-api/EdgeGuard.TelemetryApi.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:9.0
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
ENTRYPOINT ["dotnet", "EdgeGuard.TelemetryApi.dll"]
