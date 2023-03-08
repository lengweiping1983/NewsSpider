select count(*) from n_news;
select source,count(*) as num from n_news group by source order by num desc;
select source_main_category,count(*) as num from n_news group by source_main_category order by num desc;
select publish_date,count(*) as num from (select cast(publish_time as Date) as publish_date from n_news) a group by publish_date order by num desc;


insert into n_category_mapping(source,source_category,category)
select source,source_main_category,source_main_category from(
select source,source_main_category, count(*) as num from n_news_copy group by source,source_main_category order by source, num desc
) t
