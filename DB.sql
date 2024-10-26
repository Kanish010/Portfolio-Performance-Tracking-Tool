-- Create the database with case-sensitive name
CREATE DATABASE "PortfolioTrackingDB";

\c "PortfolioTrackingDB";  -- Connect to the database

-- Create "Users" table
CREATE TABLE IF NOT EXISTS "Users" (
    "user_id" SERIAL PRIMARY KEY,  -- SERIAL for auto-incremented ID
    "username" VARCHAR(50) UNIQUE NOT NULL,
    "email" VARCHAR(100) UNIQUE NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create "Portfolios" table with UUID
CREATE TABLE IF NOT EXISTS "Portfolios" (
    "portfolio_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Use UUID with automatic generation
    "user_id" INT NOT NULL REFERENCES "Users"("user_id") ON DELETE CASCADE,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE ("user_id", "name")  -- Ensure unique portfolio names per user
);

-- Create "Stocks" table with UUID for "stock_id"
CREATE TABLE IF NOT EXISTS "Stocks" (
    "stock_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- UUID with automatic generation
    "user_id" INT NOT NULL REFERENCES "Users"("user_id") ON DELETE CASCADE,
    "portfolio_id" UUID NOT NULL REFERENCES "Portfolios"("portfolio_id") ON DELETE CASCADE,
    "symbol" VARCHAR(10) NOT NULL,
    "shares" INT NOT NULL,
    "purchase_price" NUMERIC(10, 2) NOT NULL,
    "total_value" NUMERIC(10, 2) GENERATED ALWAYS AS ("shares" * "purchase_price") STORED,  -- Calculated field in PostgreSQL
    "purchase_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create "ChatHistory" table
CREATE TABLE IF NOT EXISTS "ChatHistory" (
    "id" SERIAL PRIMARY KEY,
    "session_id" UUID,
    "role" VARCHAR(10) CHECK ("role" IN ('system', 'user', 'assistant')),  -- ENUM alternative
    "content" TEXT,
    "response" TEXT,
    "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);