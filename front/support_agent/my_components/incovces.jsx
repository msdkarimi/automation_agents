import { Blockquote, Center, Box, ScrollArea, Button} from '@mantine/core';
import { IconReceiptDollar } from '@tabler/icons-react';

import { Timeline, Text } from '@mantine/core';
import { IconGitBranch, IconGitPullRequest, IconGitCommit, IconStepInto, IconMapPin, IconFlag } from '@tabler/icons-react';
import { useState } from 'react';

export function Invoces() {

  const [ckecker, SetChecker]  =  useState(0)

  const icon = <IconReceiptDollar />;
  return (
    // 1. The outer wrapper sets the maximum height.
      // This creates the boundary for our component.
      <Box className='limited-height-flex custom-font-body'>
  
        {/* 2. The inner container fills the wrapper and manages the layout.
            It now has a defined height to distribute to its children. */}
        <Blockquote color="lime" icon={icon} mt="xl" className='fill-flex-column' >
          {/* 3. The scrollable area grows to fill the remaining space.
              Since its parent (Blockquote) has a defined height, scrolling now works. */}
          <ScrollArea style={{ flexGrow: 1 }}>
          <Center  bg="var(--mantine-color-gray-light)">
            {/* <div>
            <MyTimeLine check = {ckecker} />
            <Button onClick={()=>{SetChecker(1)}}>
              Scan new QR code
            </Button>
            </div> */}
  
          </Center>
  
          </ScrollArea>
          </Blockquote>
      </Box>
    );
  }



function MyTimeLine(props) {
  return (
    <Timeline active={3} bulletSize={24} lineWidth={2}>
      <Timeline.Item bullet={<IconMapPin size={12} />} title="Start Point">
        <Text c="dimmed" size="sm"> Here you can display your environment infor like:
          <Text inherit> there is recycle bin!</Text>
          <Text inherit> there is fountaine...</Text>
        </Text>
        <Text size="xs" mt={4}>here we can display more info like which route to take, how much it take to get to next step,...</Text>
      </Timeline.Item>

      <Timeline.Item bullet={<IconStepInto size={12} />} title="Commits">
        <Text c="dimmed" size="sm">You&apos;ve pushed 23 commits to<Text variant="link" component="span" inherit>fix-notifications branch</Text></Text>
        <Text size="xs" mt={4}>52 minutes ago</Text>
      </Timeline.Item>

      <Timeline.Item title="Pull request" bullet={<IconStepInto size={12} />} lineVariant="dashed">
        <Text c="dimmed" size="sm">You&apos;ve submitted a pull request<Text variant="link" component="span" inherit>Fix incorrect notification message (#187)</Text></Text>
        <Text size="xs" mt={4}>34 minutes ago</Text>
      </Timeline.Item>


    {
      props.check != 0 ?
      <Timeline.Item title="Destination" bullet={<IconFlag size={12} />}>
       
        <Text size="xs" mt={4}>You arrived to destination!!</Text>
      </Timeline.Item>
      :
      <></>

    }
    </Timeline>
  );
}