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
ENV CORECLR_ENABLE_PROFILING=1
ENV CORECLR_PROFILER={846F5F1C-F9AE-4B07-969E-05C26BC060D8}
ENV CORECLR_PROFILER_PATH=/app/datadog/linux-x64/Datadog.Trace.ClrProfiler.Native.so
ENV DD_DOTNET_TRACER_HOME=/app/datadog
EXPOSE 8080
ENTRYPOINT ["dotnet", "EdgeGuard.TelemetryApi.dll"]
