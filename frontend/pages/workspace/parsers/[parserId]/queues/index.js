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
import ParsingQueue from '../../../../../components/queues/parsingQueue'
import SplitQueue from '../../../../../components/queues/splitQueue'
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
          <Tab id="dataSplitQueue" eventKey="dataSplitQueue" title="Split Queue">
            <SplitQueue parserId={parserId} />
          </Tab>
          <Tab id="dataParsingQueue" eventKey="dataParsingQueue" title="Data Parsing Queue">
            <ParsingQueue parserId={parserId} />
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