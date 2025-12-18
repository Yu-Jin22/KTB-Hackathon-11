# == 1. 빌드단계 ==
# gradle 빌드
FROM gradle:8.5-jdk21 AS builder

# 컨테이너 안에서 작업할 폴더 위치
WORKDIR /app

# Gradle 설정 파일들 먼저 복사
COPY build.gradle settings.gradle ./
COPY gradle gradle

# 나머지 소스 전체 복사
COPY src src

# 스프링부트 JAR 빌드
RUN gradle clean bootJar --no-daemon

# == 2. 실행단계 ==
FROM eclipse-temurin:21-jre

# 실행용 컨테이너 안 작업 폴더
WORKDIR /app

# 1단계에서 만든 JAR 파일만 가져오기
COPY --from=builder /app/build/libs/*-SNAPSHOT.jar app.jar

# 컨테이너가 여는 포트
EXPOSE 8080

# 컨테이너가 시작될 때 실행할 명령
ENTRYPOINT ["java", "-jar", "app.jar"]