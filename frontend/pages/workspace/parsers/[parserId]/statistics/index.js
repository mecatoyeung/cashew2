import { useState, useEffect } from 'react'

import { useRouter } from 'next/router'

import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

import axios from "axios";

import moment from "moment";

import DateRangePicker from 'react-bootstrap-daterangepicker';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";


import WorkspaceLayout from '../../../../../layouts/workspace'

import service from '../../../../../service'

import styles from '../../../../../styles/Statistics.module.css'

const Statistics = () => {

  const router = useRouter()

  const { parserId } = router.query

  const [parser, setParser] = useState(null)

  const [data, setData] = useState([])

  const [form, setForm] = useState({
    startDate: moment().subtract(1, 'months'),
    endDate: moment()
  })

  const getMetrics = () => {
    if (parserId == null) return
    console.log("open_ai_metrics/?parser_id=" + parserId + "&start_date=" + form.startDate.format("YYYY-MM-DD") + "&end_date=" + form.endDate.format("YYYY-MM-DD"))
    service.get("open_ai_metrics/?parser_id=" + parserId + "&start_date=" + form.startDate.format("YYYY-MM-DD") + "&end_date=" + form.endDate.format("YYYY-MM-DD"), response => {

      for (let i = 0; i < response.data.length; i++) {
        response.data[i].date = moment(
          response.data[i].date,
          "YYYY-MM-DDThh:mm:ssZ"
        ).format("YYYY-MM-DD");
      }
      
      setData(response.data)
    })
  }

  const dateEventHandler = (e, p) => {
    let updatedForm = {...form}
    updatedForm.startDate = p.startDate
    updatedForm.endDate = p.endDate
    setForm(updatedForm)
  }

  const getParser = () => {
    if (!parserId) return;
    service.get("parsers/" + parserId + "/", (response) => {
      console.log(response.data)
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
    getMetrics()
  }, [router.isReady, parserId, form.startDate, form.endDate])

  return (
    <WorkspaceLayout>
      <div className={styles.statisticsWrapper}>
        <h1>Statistics</h1>
        {parser && (
          <div className={styles.procesedPages}>
            <h2>Total Number of Pages Processed: {parser.totalNumOfPagesProcessed}</h2>
          </div>
        )}
        <h2>Azure Open AI Service Statistic</h2>
        <div className="Form">
          <Container>
            <Form>
              <DateRangePicker
                initialSettings={{ startDate: form.startDate, endDate: form.endDate }}
                onEvent={dateEventHandler}
              >
                <input type="text" className="form-control col-4" />
              </DateRangePicker>
            </Form>
          </Container>
        </div>
        <div className="TokenChart">
          <Container style={{ height: 640 }}>
            <Row style={{ height: 640 }}>
              <Col style={{ height: 640 }}>
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                  style={{ height: 640 }}
                >
                  <LineChart
                    width={500}
                    height={300}
                    data={data}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="processedTokens"
                      stroke="#8884d8"
                      activeDot={{ r: 8 }}
                      name="Processed Tokens"
                    />
                    <Line
                      type="monotone"
                      dataKey="generatedTokens"
                      stroke="#82ca9d"
                      name="Generated Tokens"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Col>
            </Row>
          </Container>
        </div>
        <div className="PricingChart">
          <Container style={{ height: 640 }}>
            <Row style={{ height: 640 }}>
              <Col style={{ height: 640 }}>
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                  style={{ height: 640 }}
                >
                  <LineChart
                    width={500}
                    height={300}
                    data={data}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="#8884d8"
                      activeDot={{ r: 8 }}
                      name="Price"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Col>
            </Row>
          </Container>
        </div>
      </div>
    </WorkspaceLayout>
  )
}

export default Statistics