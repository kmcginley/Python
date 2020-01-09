import pandas as pd
import psycopg2

def getdata():
    # sql1 = '''SELECT plate_id, jsonb_array_elements(data)->>'name' as obs, jsonb_array_elements(data)->>'value' as obsvalue,
    #             date_measured, rep_num, qr_code, well_pos, experiment_treatment_id, treatment_inputs
    #             FROM discovery.experiment_raw_data ed
    #             left join discovery.experiment_plates ep on ed.plate_id = ep.id
    #             left join discovery.experiment_treatments et on ep.experiment_treatment_id = et.id
    #             where plate_id > 66 and qr_code = '19000537_9_2' order by well_pos'''
    # sql2 = '''select t.id, 
    #             d.j ->> 'color' as color,
    #             d.j ->> 'height' as height,
    #             d.j ->> 'length' as length
    #         from the_table t
    #         left join lateral (
    #             select jsonb_object_agg(jb ->> 'name', jb ->> 'value')
    #             from jsonb_array_elements(data) e(jb)
    #         ) as d(j) on true'''

# d.j is "table d column j" and is defined in the as d(j) statement
'''inside the left join lateral, we are extracting the keys name and value, and aggregating them into
a new json object. [{'name':'leaf_health', 'value':'True'}] turns into {'leaf_health': 'True} so in the 
select statement, we can extract the key-value pairs and turn them into new columns with rows populated with
the values'''
select t.plate_id, date_measured, rep_num, qr_code, well_pos, experiment_treatment_id, treatment_inputs,
                d.j ->> 'leaf_health' as leaf_health,
                d.j ->> 'insect_area' as insect_area,
                d.j ->> 'leaf_area' as leaf_area,
                d.j ->> 'insect_mass' as insect_mass,
                d.j ->> 'comments' as comments,
                d.j ->> 'F0_survival' as F0_survival,
                d.j ->> 'plant_mass' as plant_mass
            from discovery.experiment_raw_data t
            left join lateral (
                select jsonb_object_agg(jb ->> 'name', jb ->> 'value')
                from jsonb_array_elements(data) jb) as d(j) on true
            left join discovery.experiment_plates ep on t.plate_id = ep.id
            left join discovery.experiment_treatments et on ep.experiment_treatment_id = et.id

            where plate_id > 66 and qr_code = '19000537_9_2'
            order by plate_id, well_pos, date_measured

    conn = psycopg2.connect(dbname = 'testdb', user='kmcginley', password='Dmb1412?', host='invpostgres-prod.cyjhvfnwydqi.us-east-1.rds.amazonaws.com')
    cur = conn.cursor()
    cur.execute(sql1)
    output = cur.fetchall()
    conn.close()

    df = pd.DataFrame(output)
    # df2 = df[[0,1,2,3]]
    # df = df[[0,4,5,6,7]].drop_duplicates()
    
    print(df)
    # print(df2.T)

if __name__ == "__main__":
    getdata()