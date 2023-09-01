import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

def compute_graph(worklogs,employees):
    fig = go.Figure()
    if len(worklogs)>0:
        worklogs = pd.read_json(worklogs)
        employees = pd.read_json(employees)

        if worklogs.size > 0:

            grouped_data = worklogs.groupby('weekstarted')['time_hours'].sum()

            week = grouped_data.index
            hours = grouped_data.values

            def percent_total_hours(date, percent):
                
                #filter total hours for given week by checking that date lies within the start and end dates of employees
                mask = (employees['start_date'] <= date) & ((employees['end_date'].isna()) | (employees['end_date'] >= date))

                #print("DATE:",date)
                #print("Employees counted:")
                #print(self.employees[mask])

                percent_total_hours = employees[mask]['hours_pw'].sum()*percent

                return percent_total_hours

            PX_WHRS = 0.8

            grouped_data['percent_total_hours'] = grouped_data.index.map( lambda date: percent_total_hours(date, PX_WHRS) )

            #print(grouped_data)

            fig = px.line(x=week, y=grouped_data['percent_total_hours'], color=px.Constant(f"{PX_WHRS*100:.0f}% Working Hours"))
            fig.add_bar(x=week, y=hours, name="Actual Logged Hours")

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Weeks",
                yaxis_title="Hours",
            )
        else: 
            fig.update_layout(template = None)
            fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
            fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig