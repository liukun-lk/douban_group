require "logger"
require "sequel/core"
require 'dotenv/load'

namespace :db do
  desc "Run migrations"
  task :migrate, [:version] do |t, args|
    Sequel.extension :migration
    version = args[:version].to_i if args[:version]
    Sequel.connect("#{ENV.fetch("DATABASE_HOST")}/#{ENV.fetch('DATABASE')}", logger: Logger.new($stderr)) do |db|
      Sequel::Migrator.run(db, "db/migrations", target: version)
    end
  end

  desc 'Create database'
  task :create, [:version] do
    Sequel.connect("#{ENV.fetch("DATABASE_HOST")}", logger: Logger.new($stderr)) do |db|
      db.execute "CREATE DATABASE #{ENV.fetch("DATABASE")}"
    end
  end

  desc 'Drop database'
  task :drop, [:version] do
    Sequel.connect("#{ENV.fetch("DATABASE_HOST")}/#{ENV.fetch('DATABASE')}", logger: Logger.new($stderr)) do |db|
      db.execute "DROP DATABASE IF EXISTS #{ENV.fetch("DATABASE")}"
    end
  end
end
