import { useEffect } from 'react'

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
import OCRQueue from '../../../../../components/queues/ocrQueue'
import ParsingQueue from '../../../../../components/queues/parsingQueue'
import SplittingQueue from '../../../../../components/queues/splittingQueue'
import PostProcessingQueue from '../../../../../components/queues/postProcessingQueue'
import IntegrationQueue from '../../../../../components/queues/integrationQueue'

import styles from '../../../../../styles/Parser.module.css'

const ParserDocuments = () => {

  const router = useRouter()

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  const { parserId } = router.query

  return (
    <WorkspaceLayout>
      <div className={styles.documentsQueueTabWrapper}>
        <Tabs id="Queues" defaultActiveKey="importQueue">
          <Tab id="processedQueue" eventKey="processedQueue" title="Processed Queue">
            <ProcessedQueue parserId={parserId} />
          </Tab>
          <Tab id="importQueue" eventKey="importQueue" title="Import Queue">
            <ImportQueue parserId={parserId} />
          </Tab>
          <Tab id="dataSplitQueue" eventKey="dataOCRQueue" title="OCR Queue">
            <OCRQueue parserId={parserId} />
          </Tab>
          <Tab id="dataSplitingQueue" eventKey="dataSplitQueue" title="Splitting Queue">
            <SplittingQueue parserId={parserId} />
          </Tab>
          <Tab id="dataParsingQueue" eventKey="dataParsingQueue" title="Parsing Queue">
            <ParsingQueue parserId={parserId} />
          </Tab>
          <Tab id="postProcessingQueue" eventKey="postProcessingQueue" title="Post Processing Queue">
            <PostProcessingQueue parserId={parserId} />
          </Tab>
          <Tab id="integrationQueue" eventKey="integrationQueue" title="Integration Queue">
            <IntegrationQueue parserId={parserId} />
          </Tab>
        </Tabs>
      </div>
    </WorkspaceLayout>
  )
}

export default ParserDocuments