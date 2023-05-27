import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { Button } from 'react-bootstrap'

import WorkspaceLayout from '../../../layouts/workspace'

import parsersStyles from "../../../styles/Parsers.module.scss"

export default function Parsers() {

  const router = useRouter()

  return (
    <WorkspaceLayout>
      <ul className={parsersStyles.parsersUl}>
        <li>
          <div className={parsersStyles.parserName} onClick={() => router.push("workspace/parsers/1")}>KOHLS</div>
          <div className={parsersStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
        <li>
          <div className={parsersStyles.parserName} onClick={() => router.push("workspace/parsers/1")}>Gaps & Old Navy</div>
          <div className={parsersStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
        <li>
          <div className={parsersStyles.parserName} onClick={() => router.push("workspace/parsers/1")}>Zuru</div>
          <div className={parsersStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
      </ul>
    </WorkspaceLayout>
  )
}
