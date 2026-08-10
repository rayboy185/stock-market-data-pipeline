with stocks as (
    select * from {{ ref('stg_stocks') }}
),

macro as (
    select * from {{ ref('stg_macro') }}
),

signals as (
    select
        s.date,
        s.ticker,
        s.open,
        s.high,
        s.low,
        s.close,
        s.volume,

        -- Daily return %
        round(
            ((s.close - lag(s.close) over (partition by s.ticker order by s.date))
            / lag(s.close) over (partition by s.ticker order by s.date) * 100)::numeric, 2
        ) as daily_return_pct,

        -- 7-day moving average
        round(
            avg(s.close) over (
                partition by s.ticker
                order by s.date
                rows between 6 preceding and current row
            )::numeric, 2
        ) as ma_7d,

        -- 30-day moving average
        round(
            avg(s.close) over (
                partition by s.ticker
                order by s.date
                rows between 29 preceding and current row
            )::numeric, 2
        ) as ma_30d,

        -- Volume spike — is today's volume 50% above 30-day average?
        case
            when s.volume > 1.5 * avg(s.volume) over (
                partition by s.ticker
                order by s.date
                rows between 29 preceding and current row
            ) then true
            else false
        end as volume_spike,

        -- Price above 7d MA signal
        case
            when s.close > avg(s.close) over (
                partition by s.ticker
                order by s.date
                rows between 6 preceding and current row
            ) then 'above'
            else 'below'
        end as price_vs_ma7,

        -- Macro context
        m.us_10y_yield,
        m.us_inflation_proxy,
        m.uk_10y_yield

    from stocks s
    left join macro m on s.date = m.date
)

select * from signals