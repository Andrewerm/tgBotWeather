import os

import ydb

from tgbot.config import load_config

config = load_config()


def create_table(session, path):
    session.create_table(
        os.path.join(path, 'series'),
        ydb.TableDescription()
        .with_column(ydb.Column('series_id', ydb.PrimitiveType.Uint64))  # not null column
        .with_column(ydb.Column('title', ydb.OptionalType(ydb.PrimitiveType.Utf8)))
        .with_column(ydb.Column('series_info', ydb.OptionalType(ydb.PrimitiveType.Utf8)))
        .with_column(ydb.Column('release_date', ydb.OptionalType(ydb.PrimitiveType.Uint64)))
        .with_primary_key('series_id')
    )


def delete_table(session, path):
    session.drop_table(path)


def describe_table(session, path, name):
    result = session.describe_table(os.path.join(path, name))
    print("\n> describe table: series")
    for column in result.columns:
        print("column, name:", column.name, ",", str(column.type.item).strip())


def run(driver_config):
    with ydb.Driver(driver_config) as driver:
        try:
            driver.wait(timeout=5)
            description = (
                ydb.TableDescription()
                .with_primary_keys('key1', 'key2')
                .with_columns(
                    ydb.Column('key1', ydb.OptionalType(ydb.PrimitiveType.Uint64)),
                    ydb.Column('key2', ydb.OptionalType(ydb.PrimitiveType.Uint64)),
                    ydb.Column('value', ydb.OptionalType(ydb.PrimitiveType.Utf8))
                )
                .with_profile(
                    ydb.TableProfile()
                    .with_partitioning_policy(
                        ydb.PartitioningPolicy()
                        .with_explicit_partitions(
                            ydb.ExplicitPartitions(
                                (
                                    ydb.KeyBound((100,)),
                                    ydb.KeyBound((300, 100)),
                                    ydb.KeyBound((400,)),
                                )
                            )
                        )
                    )
                )
            )

            session = driver.table_client.session().create()
            session.create_table('/series', description)
        except TimeoutError:
            print("Connect failed to YDB")
            print("Last reported errors by discovery:")
            print(driver.discovery_debug_details())
            exit(1)


if __name__ == '__main__':
    run(config.yadb.db_config)
