import { useState, useEffect } from 'react'

import { useRouter } from 'next/router'

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'

import WorkspaceLayout from '../../../../../layouts/workspace'
import ParserLayout from '../../../../../layouts/parser'

import ProcessedQueue from '../../../../../components/queues/processedQueue'
import ImportQueue from '../../../../../components/queues/importQueue'
import PreProcessingQueue from '../../../../../components/queues/preProcessingQueue'
import OCRQueue from '../../../../../components/queues/ocrQueue'
import ParsingQueue from '../../../../../components/queues/parsingQueue'
import SplittingQueue from '../../../../../components/queues/splittingQueue'
import PostProcessingQueue from '../../../../../components/queues/postProcessingQueue'
import IntegrationQueue from '../../../../../components/queues/integrationQueue'

import service from '../../../../../service'

import styles from '../../../../../styles/Parser.module.css'

const ParserDocuments = () => {

  const router = useRouter()

  const { parserId } = router.query

  const [processedQueues, setProcessedQueues] = useState([])
  const [importQueues, setImportQueues] = useState([])
  const [preProcessingQueues, setPreProcessingQueues] = useState([])
  const [ocrQueues, setOCRQueues] = useState([])
  const [splittingQueues, setSplittingQueues] = useState([])
  const [parsingQueues, setParsingQueues] = useState([])
  const [postProcessingQueues, setPostProcessingQueues] = useState([])
  const [integrationQueues, setIntegrationQueues] = useState([])

  const getProcessedQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=PROCESSED",
      (response) => {
        setProcessedQueues(response.data);
      }
    )
  }

  const getImportQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=IMPORT",
      (response) => {
        setImportQueues(response.data);
      }
    )
  }

  const getPreProcessingQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=PRE_PROCESSING",
      (response) => {
        setPreProcessingQueues(response.data);
      }
    )
  }

  const getOCRQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=OCR",
      (response) => {
        setOCRQueues(response.data);
      }
    )
  }

  const getSplittingQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=SPLITTING",
      (response) => {
        setSplittingQueues(response.data);
      }
    )
  }

  const getParsingQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=PARSING",
      (response) => {
        setParsingQueues(response.data);
      }
    )
  }

  const getPostProcessingQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=POST_PROCESSING",
      (response) => {
        setPostProcessingQueues(response.data);
      }
    )
  }

  const getIntegrationQueues = () => {
    if (!parserId) return;
    service.get(
      "queues/?parserId=" + parserId + "&queueClass=INTEGRATION",
      (response) => {
        setIntegrationQueues(response.data);
      }
    )
  }

  useEffect(() => {
    if (!router.isReady) return
    getProcessedQueues()
    getImportQueues()
    getPreProcessingQueues()
    getOCRQueues()
    getSplittingQueues()
    getParsingQueues()
    getPostProcessingQueues()
    getIntegrationQueues()
    const interval = setInterval(() => {
      getProcessedQueues()
      getImportQueues()
      getPreProcessingQueues()
      getOCRQueues()
      getSplittingQueues()
      getParsingQueues()
      getPostProcessingQueues()
      getIntegrationQueues()
    }, 5000);
  }, [router.isReady])

  return (
    <WorkspaceLayout>
      <div className={styles.documentsQueueTabWrapper}>
        <Tabs id="Queues" defaultActiveKey="importQueue">
          <Tab id="processedQueue" eventKey="processedQueue" title={"Processed Queue (" + processedQueues.length + ")"}>
            <ProcessedQueue parserId={parserId} queues={processedQueues}/>
          </Tab>
          <Tab id="importQueue" eventKey="importQueue" title={"Import Queue (" + importQueues.length + ")"}>
            <ImportQueue parserId={parserId} queues={importQueues} />
          </Tab>
          <Tab id="preProcessingQueue" eventKey="preProcessingQueue" title={"Pre Processing Queue (" + preProcessingQueues.length + ")"}>
            <PreProcessingQueue parserId={parserId} queues={preProcessingQueues} />
          </Tab>
          <Tab id="dataSplitQueue" eventKey="dataOCRQueue" title={"OCR Queue (" + ocrQueues.length + ")"}>
            <OCRQueue parserId={parserId} queues={ocrQueues} />
          </Tab>
          <Tab id="dataSplitingQueue" eventKey="dataSplitQueue" title={"Splitting Queue (" + splittingQueues.length + ")"}>
            <SplittingQueue parserId={parserId} queues={splittingQueues} />
          </Tab>
          <Tab id="dataParsingQueue" eventKey="dataParsingQueue" title={"Parsing Queue (" + parsingQueues.length + ")"}>
            <ParsingQueue parserId={parserId} queues={parsingQueues} />
          </Tab>
          <Tab id="postProcessingQueue" eventKey="postProcessingQueue" title={"Post Processing Queue (" + postProcessingQueues.length + ")"}>
            <PostProcessingQueue parserId={parserId} queues={postProcessingQueues} />
          </Tab>
          <Tab id="integrationQueue" eventKey="integrationQueue" title={"Integration Queue (" + integrationQueues.length + ")"}>
            <IntegrationQueue parserId={parserId} queues={integrationQueues} />
          </Tab>
        </Tabs>
      </div>
    </WorkspaceLayout>
  )
}

export default ParserDocuments