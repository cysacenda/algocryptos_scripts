-- Table: public.coins

-- DROP TABLE public.coins;

CREATE TABLE public.coins
(
    "IdCryptoCompare" bigint,
    "Name" text COLLATE pg_catalog."default",
    "Symbol" character varying(9) COLLATE pg_catalog."default",
    "CoinName" text COLLATE pg_catalog."default",
    "TotalCoinSupply" text COLLATE pg_catalog."default",
    "SortOrder" integer,
    "ProofType" text COLLATE pg_catalog."default",
    "Algorithm" text COLLATE pg_catalog."default",
    "ImageUrl" text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.coins
    OWNER to postgres;

GRANT ALL ON TABLE public.coins TO dbuser;
GRANT ALL ON TABLE public.coins TO postgres;

COMMENT ON TABLE public.coins
    IS 'Contains one line per cryptocurrency, data comes from Cryptocompare';

-- Table: public.prices

-- DROP TABLE public.prices;

CREATE TABLE public.prices
(
    "IdCryptoCompare" bigint,
    Symbol character varying(9) COLLATE pg_catalog."default" NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    Rank integer,
    Price_usd double precision,
    Price_btc double precision,
    "24h_volume_usd" double precision,
    Market_cap_usd double precision,
    Percent_change_1h double precision,
    Percent_change_24h double precision,
    Percent_change_7d double precision,
    Last_updated timestamp with time zone
    -- CONSTRAINT prices_pkey PRIMARY KEY (Symbol)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.prices
    OWNER to postgres;

GRANT ALL ON TABLE public.prices TO dbuser;
GRANT ALL ON TABLE public.prices TO postgres;

COMMENT ON TABLE public.prices
    IS 'Contains one line per cryptocurrency, data comes from CoinMarketCap';

-- Table: public.social_infos

-- DROP TABLE public.social_infos;

CREATE TABLE public.social_infos
(
    "IdCoinCryptoCompare" bigint,
    "Twitter_account_creation" timestamp with time zone,
    "Twitter_name" text COLLATE pg_catalog."default",
    "Twitter_link" text COLLATE pg_catalog."default",
    "Reddit_name" text COLLATE pg_catalog."default",
    "Reddit_link" text COLLATE pg_catalog."default",
    "Reddit_community_creation" timestamp with time zone,
    "Facebook_name" text COLLATE pg_catalog."default",
    "Facebook_link" text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_infos
    OWNER to postgres;

GRANT ALL ON TABLE public.social_infos TO dbuser;
GRANT ALL ON TABLE public.social_infos TO postgres;

COMMENT ON TABLE public.social_infos
    IS 'Contains one line per cryptocurrency with informations relatives to social networks of the cryptocurrency, data comes from CryptoCompare';

-- Table: public.social_stats

-- DROP TABLE public.social_stats;

CREATE TABLE public.social_stats
(
    "IdCoinCryptoCompare" bigint,
    "Twitter_followers" bigint,
    "Reddit_posts_per_day" double precision,
    "Reddit_comments_per_day" double precision,
    "Reddit_active_users" bigint,
    "Reddit_subscribers" bigint,
    "Facebook_likes" bigint,
    "Facebook_talking_about" bigint,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats
    OWNER to postgres;

GRANT ALL ON TABLE public.social_stats TO dbuser;
GRANT ALL ON TABLE public.social_stats TO postgres;


COMMENT ON TABLE public.social_stats
    IS 'Contains one line per cryptocurrency with informations relatives to social networks statistics about the cryptocurrency, data comes from CryptoCompare; For information related to Reddit, use social_stats_reddit table, not this one';

-- User !
--GRANT ALL ON TABLE public.coins TO dbuser;
--GRANT ALL ON TABLE public.coins TO postgres;

-- Table: public.social_stats_reddit

-- DROP TABLE public.social_stats_reddit;

CREATE TABLE public.social_stats_reddit
(
    "IdCoinCryptoCompare" bigint,
    "Reddit_subscribers" bigint,
    "Reddit_active_users" bigint,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats_reddit
    OWNER to postgres;

CREATE INDEX social_stats_reddit_index
ON social_stats_reddit ("IdCoinCryptoCompare");

GRANT ALL ON TABLE public.social_stats_reddit TO dbuser;
GRANT ALL ON TABLE public.social_stats_reddit TO postgres;


COMMENT ON TABLE public.social_stats_reddit
    IS 'Contains one line per cryptocurrency per date with statistic on th subreddit of the cryptocurrency, data comes from redditmetrics.com (historical data) and reddit.com/subredditname/about.json for real time data';



-- Table: public.histo_ohlcv

-- DROP TABLE public.histo_ohlcv;

CREATE TABLE public.histo_ohlcv
(
    "IdCoinCryptoCompare" bigint NOT NULL,
    "open" double precision,
    "high" double precision,
    "low" double precision,
    "close" double precision,
    "volume_aggregated" double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.histo_ohlcv
    OWNER to postgres;

GRANT ALL ON TABLE public.histo_ohlcv TO dbuser;
GRANT ALL ON TABLE public.histo_ohlcv TO postgres;

COMMENT ON TABLE public.histo_ohlcv
    IS 'Contains one line per cryptocurrency per date per hour with informations on OHLC and the volumes of the cryptocurrency, data comes from CryptoCompare and volumes are calculated on an aggregate of main trading pairs (so it s not the global volume, but we are looking for trends, so ok';


-- Table: public.excluded_coins

-- DROP TABLE public.excluded_coins;

CREATE TABLE public.excluded_coins
(
    "IdCoinCryptoCompare" bigint NOT NULL
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.excluded_coins
    OWNER to postgres;

GRANT ALL ON TABLE public.excluded_coins TO dbuser;
GRANT ALL ON TABLE public.excluded_coins TO postgres;

COMMENT ON TABLE public.excluded_coins
    IS 'This table contains the list of cryptocurrencies we want to exclude from the tool - inactive, useless, etc.';


-- Table: public.social_infos_manual

-- DROP TABLE public.social_infos_manual;


CREATE TABLE public.social_infos_manual
(
    "IdCoinCryptoCompare" bigint NOT NULL,
    "Reddit_name" text COLLATE pg_catalog."default",
    "Twitter_link" text COLLATE pg_catalog."default",
    "Facebook_link" text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_infos_manual
    OWNER to postgres;

GRANT ALL ON TABLE public.social_infos_manual TO dbuser;

GRANT ALL ON TABLE public.social_infos_manual TO postgres;

COMMENT ON TABLE public.social_infos_manual
    IS 'Contains one line per cryptocurrency with informations relatives to social networks of the cryptocurrency which are not provided by CryptoCompare and are retrieved manually by us';

-- Table: public.histo_prices

-- DROP TABLE public.histo_prices;


CREATE TABLE public.histo_prices
(
    "IdCryptoCompare" bigint,
    Symbol character varying(9) COLLATE pg_catalog."default" NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    Price_usd double precision,
    Price_btc double precision,
    "24h_volume_usd" double precision,
    Market_cap_usd double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.histo_prices
    OWNER to postgres;

GRANT ALL ON TABLE public.histo_prices TO dbuser;
GRANT ALL ON TABLE public.histo_prices TO postgres;

COMMENT ON TABLE public.histo_prices
    IS 'Contains one line per cryptocurency with informations relatives to social networks of the cryptocurrency which are not provided by CryptoCompare and are retrieved manually by us';


-- Table: public.kpi_reddit_subscribers

-- DROP TABLE public.kpi_reddit_subscribers;


CREATE TABLE public.kpi_reddit_subscribers
(
    "IdCryptoCompare" bigint,
    subscribers_1d_trend double precision,
    subscribers_3d_trend double precision,
    subscribers_7d_trend double precision,
    subscribers_15d_trend double precision,
    subscribers_30d_trend double precision,
    subscribers_60d_trend double precision,
    subscribers_90d_trend double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_reddit_subscribers
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_reddit_subscribers TO dbuser;
GRANT ALL ON TABLE public.kpi_reddit_subscribers TO postgres;

COMMENT ON TABLE public.kpi_reddit_subscribers
    IS 'Contains one line per cryptocurency with kpis on reddit subscribers, store only last kpi calcul';


-- Table: public.kpi_reddit_subscribers

-- DROP TABLE public.kpi_reddit_subscribers;


CREATE TABLE public.kpi_reddit_subscribers_histo
(
    "IdCryptoCompare" bigint,
    subscribers_1d_trend double precision,
    subscribers_3d_trend double precision,
    subscribers_7d_trend double precision,
    subscribers_15d_trend double precision,
    subscribers_30d_trend double precision,
    subscribers_60d_trend double precision,
    subscribers_90d_trend double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_reddit_subscribers_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_reddit_subscribers_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_reddit_subscribers_histo TO postgres;

COMMENT ON TABLE public.kpi_reddit_subscribers_histo
    IS 'Contains one line per cryptocurency with kpis on reddit subscribers, store all historic of KPI';


-- Table: public.process_params

-- DROP TABLE public.process_params;

CREATE TABLE public.process_params
(
    "IdProcess" integer NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    "Status" text COLLATE pg_catalog."default",
	"timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.process_params
    OWNER to postgres;

GRANT ALL ON TABLE public.process_params TO dbuser;
GRANT ALL ON TABLE public.process_params TO postgres;

COMMENT ON TABLE public.process_params
    IS 'Allow to avoid some processes to run at the same time';

-- Table: public.ath_prices

-- DROP TABLE public.ath_prices;

CREATE TABLE public.ath_prices
(
    "IdCryptoCompare" bigint,
    "Name" text COLLATE pg_catalog."default",
    Prices_ath_usd double precision,
    Ath_date timestamp with time zone,
    Last_updated timestamp with time zone
    -- CONSTRAINT prices_pkey PRIMARY KEY (Symbol)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.ath_prices
    OWNER to postgres;

GRANT ALL ON TABLE public.ath_prices TO dbuser;
GRANT ALL ON TABLE public.ath_prices TO postgres;

COMMENT ON TABLE public.ath_prices
    IS 'Contains one line per cryptocurrency with ATH et ATH date';

-- Table: public.top_cryptos

-- DROP TABLE public.top_cryptos;

CREATE TABLE public.top_cryptos
(
    "IdCryptoCompare" bigint
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.top_cryptos
    OWNER to postgres;

GRANT ALL ON TABLE public.top_cryptos TO dbuser;
GRANT ALL ON TABLE public.top_cryptos TO postgres;

COMMENT ON TABLE public.top_cryptos
    IS 'Contains one line per cryptocurrency which are top currencies (usefull for trading pairs count)';


-- Table: public.process_params_histo

-- DROP TABLE public.process_params_histo;

CREATE TABLE public.process_params_histo
(
    "IdProcess" integer NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    "Status" text COLLATE pg_catalog."default",
	"timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.process_params_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.process_params_histo TO dbuser;
GRANT ALL ON TABLE public.process_params_histo TO postgres;

COMMENT ON TABLE public.process_params_histo
    IS 'Historical data of processes with status';

-- Table: public.social_stats_reddit_histo

-- DROP TABLE public.social_stats_reddit_histo;

CREATE TABLE public.social_stats_reddit_histo
(
    "IdCoinCryptoCompare" bigint,
    "Reddit_subscribers" bigint,
    "Reddit_active_users" bigint,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats_reddit_histo
    OWNER to postgres;

CREATE INDEX social_stats_reddit_histo_index
ON social_stats_reddit_histo ("IdCoinCryptoCompare");

GRANT ALL ON TABLE public.social_stats_reddit_histo TO dbuser;
GRANT ALL ON TABLE public.social_stats_reddit_histo TO postgres;

COMMENT ON TABLE public.social_stats_reddit_histo
    IS 'Contains one line per cryptocurrency per date with statistic on th subreddit of the cryptocurrency, data comes from redditmetrics.com (historical data) and reddit.com/subredditname/about.json for real time data';


-- DROP TABLE public.global_data;

CREATE TABLE public.global_data
(
    total_market_cap_usd double precision,
    total_24h_volume_usd double precision,
    bitcoin_percentage_of_market_cap double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.global_data
    OWNER to postgres;

GRANT ALL ON TABLE public.global_data TO dbuser;
GRANT ALL ON TABLE public.global_data TO postgres;

COMMENT ON TABLE public.global_data
    IS 'Contains global data from CMC like global market cap etc.';


-- DROP TABLE public.kpi_market_volumes;

CREATE TABLE public.kpi_market_volumes
(
    "IdCoinCryptoCompare" bigint,
    "volume_mean_last_1h_vs_30d" double precision,
    "volume_mean_last_3h_30d" double precision,
    "volume_mean_last_6h_30d" double precision,
    "volume_mean_last_12h_30d" double precision,
    "volume_mean_last_24h_30d" double precision,
    "volume_mean_last_3d_30d" double precision,
    "volume_mean_last_7d_30d" double precision,
    "timestamp" timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_market_volumes
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_market_volumes TO dbuser;
GRANT ALL ON TABLE public.kpi_market_volumes TO postgres;

COMMENT ON TABLE public.kpi_market_volumes
    IS 'Contains market kpis about volumes.';


-- DROP TABLE public.kpi_market_volumes_histo;

CREATE TABLE public.kpi_market_volumes_histo
(
    "IdCoinCryptoCompare" bigint,
    "volume_mean_last_1h_vs_30d" double precision,
    "volume_mean_last_3h_30d" double precision,
    "volume_mean_last_6h_30d" double precision,
    "volume_mean_last_12h_30d" double precision,
    "volume_mean_last_24h_30d" double precision,
    "volume_mean_last_3d_30d" double precision,
    "volume_mean_last_7d_30d" double precision,
    "timestamp" timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_market_volumes_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_market_volumes_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_market_volumes_histo TO postgres;

COMMENT ON TABLE public.kpi_market_volumes_histo
    IS 'Contains historical data of market kpis about volumes.';


-- DROP TABLE public.process_description;

CREATE TABLE public.process_description
(
    "Name" text COLLATE pg_catalog."default",
    "Description" text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.process_description
    OWNER to postgres;

GRANT ALL ON TABLE public.process_description TO dbuser;
GRANT ALL ON TABLE public.process_description TO postgres;

COMMENT ON TABLE public.process_description
    IS 'Contains description of processes.';

-- Table: public.lower_higher_prices

-- DROP TABLE public.lower_higher_prices;

CREATE TABLE public.lower_higher_prices
(
    "IdCryptoCompare" bigint,
    price_low_15d double precision,
    date_low_15d timestamp with time zone,
    price_low_1m double precision,
    date_low_1m timestamp with time zone
    --TODO : A finir
    -- CONSTRAINT prices_pkey PRIMARY KEY (Symbol)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.lower_higher_prices
    OWNER to postgres;

GRANT ALL ON TABLE public.lower_higher_prices TO dbuser;
GRANT ALL ON TABLE public.lower_higher_prices TO postgres;

COMMENT ON TABLE public.lower_higher_prices
    IS 'Contains one line per cryptocurrency with lowers and highers on different periods';