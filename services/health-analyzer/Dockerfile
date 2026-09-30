FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY Directory.Build.props ./
COPY shared/EdgeGuard.Shared/ shared/EdgeGuard.Shared/
COPY services/health-analyzer/ services/health-analyzer/
RUN dotnet publish services/health-analyzer/EdgeGuard.HealthAnalyzer.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/runtime:9.0
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "EdgeGuard.HealthAnalyzer.dll"]
