CREATE DATABASE nyt_wordle;
CREATE DATABASE nyt_connections;
CREATE DATABASE nyt_strands;
CREATE DATABASE nyt_pips;


-- users table (shared pattern)
CREATE TABLE IF NOT EXISTS nyt_wordle.users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(255),
  UNIQUE KEY uq_user_id(user_id)
);

-- wordle entries
CREATE TABLE IF NOT EXISTS nyt_wordle.entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  puzzle_id INT NOT NULL,
  user_id BIGINT NOT NULL,
  score INT,
  green INT,
  yellow INT,
  other INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_puzzle_user(puzzle_id,user_id)
);

-- users table (shared pattern)
CREATE TABLE IF NOT EXISTS nyt_connections.users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(255),
  UNIQUE KEY uq_user_id(user_id)
);

-- connections entries
CREATE TABLE IF NOT EXISTS nyt_connections.entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  puzzle_id INT NOT NULL,
  user_id BIGINT NOT NULL,
  score INT,
  puzzle_str TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_puzzle_user(puzzle_id,user_id)
);

-- users table (shared pattern)
CREATE TABLE IF NOT EXISTS nyt_strands.users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(255),
  UNIQUE KEY uq_user_id(user_id)
);

-- strands entries
CREATE TABLE IF NOT EXISTS nyt_strands.entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  puzzle_id INT NOT NULL,
  user_id BIGINT NOT NULL,
  hints INT,
  puzzle_str TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_puzzle_user(puzzle_id,user_id)
);


-- users table (shared pattern)
CREATE TABLE IF NOT EXISTS nyt_pips.users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(255),
  UNIQUE KEY uq_user_id(user_id)
);

CREATE TABLE IF NOT EXISTS nyt_pips.entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  puzzle_id INT NOT NULL,
  user_id BIGINT NOT NULL,
  easy_seconds INT,
  medium_seconds INT,
  hard_seconds INT,
  easy_cookie BOOLEAN,
  medium_cookie BOOLEAN,
  hard_cookie BOOLEAN,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_puzzle_user(puzzle_id,user_id)
);
