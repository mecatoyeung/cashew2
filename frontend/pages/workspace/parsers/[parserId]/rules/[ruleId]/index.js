import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

import EditorLayout from '../../../../../../layouts/editor'

import RuleProperties from '../../../../../../components/ruleEditor/ruleProperties'
import RegionSelector from '../../../../../../components/ruleEditor/regionSelector'

const RuleEditor = () => {

    const router = useRouter()

    let { type = "ruleProperties" } = router.query

    useEffect(() => {
    }, [router.isReady])

    return (
        <>
            {type == "ruleProperties" && (
                <RuleProperties />
            )}
            {type == "regionSelector" && (
                <RegionSelector />
            )}
            {type == "streamEditor" && (
                <StreamEditor />
            )}
        </>
    )

}

export default RuleEditor