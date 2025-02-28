FROM gitpod/workspace-full:latest

# Switch to root user for commands requiring elevated permissions
USER root

# Install Node.js and npm (Node.js 20 LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest # Optional: Update npm to the latest version

# Install Docker and Docker Compose
RUN apt-get update && apt-get install -y docker.io docker-compose \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configure Docker to run without sudo
RUN groupadd -f docker && usermod -aG docker gitpod

# Pre-install project dependencies (Optional)
COPY package*.json ./
RUN npm install # Replace with `yarn install` if using Yarn

# Switch back to the default non-root user
USER gitpod
