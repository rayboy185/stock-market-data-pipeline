with us_yield as (
    SELECT
       date::date as date,
       us_10y_yield::float as us_10y_yield
         FROM raw_us_yield
         where us_10y_yield is not null
),

us_inflation as (
    SELECT
         date::date as date,
         us_inflation_proxy::float as us_inflation_proxy
             from raw_us_inflation
             where  us_inflation_proxy is not null
),

uk_yield as (
    SELECT
       date::date as date,
       uk_10y_yield::float as uk_10y_yield
         FROM raw_uk_yield
         where uk_10y_yield is not null
)

select
    u.date,
    u.us_10y_yield,
    i.us_inflation_proxy,
    k.uk_10y_yield
    from us_yield u
    left join us_inflation i on u.date = i.date
    left join uk_yield k on u.date = k.date