with source as (SELECT
     date::date as date,
     ticker,
     open::float as open,
     high::float as high,
     low::float as low,
     close::float as close,
     volume
     from raw_stocks
     where close is not null
     ),

deduped as (
      select *,
        row_number() over (
            partition by date, ticker
            order by date
        ) as row_num
        from source
)

select
date,
ticker,
open,
high,
low,
close,
volume
from deduped
where row_num = 1
